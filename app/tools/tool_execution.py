import logging
import re
from asyncio import sleep
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from app.config.config import Config
from app.models.state_model import WorkflowState
from app.services.user_notification_service import UserNotificationService
from app.utils.get_tokens_from_mesaages import GetMessageTokens


class ToolExecution:
    def __init__(self, llm_service):
        self.llm_service = llm_service
        self.PROMPT_TOKENS = 0
        self.COMPLETION_TOKENS = 0

    async def run(self, state: WorkflowState):
        logging.info("ToolExecution started.")

        for step_name, tool, tool_input in state.steps:
            if step_name not in state.completed_steps:
                try:
                    logging.info(f"Executing step: {step_name} with tool: {tool}")
                    results_temp = state.results

                    if "#" in tool_input:
                        tool_input = await self._resolve_references(tool_input=tool_input,
                                                                    results=results_temp,
                                                                    current_tool=tool)
                    # Aracı çalıştır ve sonucu al
                    # result = await self.execute_tool(tool, tool_input)
                    state.results[step_name] = await self.execute_tool(tool, tool_input)
                    state.completed_steps.add(step_name)

                except Exception as e:
                    logging.error(f"Error in ToolExecution: {str(e)}")
                    break

        state.prompt_tokens += self.PROMPT_TOKENS
        state.completion_tokens += self.COMPLETION_TOKENS

        logging.info("ToolExecution finished.")
        return state

    async def execute_tool(self, tool, tool_input):
        """Verilen aracı ve girişi çalıştırır ve sonucu döndürür."""
        try:
            if tool == "web_search":
                logging.info(f"Executing web_search tool")
                if tool_input is None:
                    logging.warning("Web search tool input is empty.")
                    return {"link": "", "snippet": "Web search input is empty."}
                return await self._web_search(tool_input)

            elif tool == "parser":
                logging.info(f"Executing parser tool")

                if tool_input is None:
                    logging.warning("Parser tool input is empty.")
                    return {"title": "No input", "content": "Parser tool input is empty."}

                if isinstance(tool_input, list):
                    # Eğer tool_input bir listeyse, her URL'yi ayrı ayrı işlemeye başlıyoruz
                    parsed_results = []
                    for url in tool_input:
                        # parsed_result = await self._parser(url)  # Her URL için parser fonksiyonunu çağır
                        parsed_results.append(await self._parser(url))
                    return parsed_results  # Tüm sonuçları liste olarak döndür
                else:
                    return await self._parser(tool_input)  # Tek bir URL varsa doğrudan işle

            elif tool == "LLM":
                logging.info(f"Executing LLM tool")

                if tool_input is None:
                    logging.warning("LLM tool input is empty.")
                    return "LLM tool input is empty."

                result = await self.llm_service.invoke(prompt=tool_input)

                prompt_tokens, completion_tokens = GetMessageTokens.get_tokens_from_messages(message=result)
                self._update_tokens(prompt_tokens, completion_tokens)

                return result.content

            else:
                logging.warning(f"Unknown tool: {tool}")
                return f"Unknown tool: {tool}"

        except Exception as e:
            logging.error(f"Error in execute_tool: {str(e)}")
            return f"Error occurred during tool execution: {str(e)}"

    def _update_tokens(self, prompt_tokens, completion_tokens):
        """Token bilgilerini günceller."""
        self.PROMPT_TOKENS += prompt_tokens
        self.COMPLETION_TOKENS += completion_tokens

    @staticmethod
    async def _resolve_references(tool_input, results, current_tool):
        """
        tool_input içindeki referansları (#E1, #E2 gibi) çözer ve birleştirir.
        Hangi alanın alınacağı (snippet veya link), mevcut aracın ve referans edilen adımın
        türüne bağlıdır.

        Args:
            tool_input (str): Mevcut adımın girdisi.
            results (dict): Daha önceki adımların sonuçlarını içeren sözlük.
            current_tool (str): Mevcut adımda kullanılan araç (ör. LLM, parser).

        Returns:
            str or list: Çözülmüş ve birleştirilmiş veriler.
        """
        if isinstance(tool_input, str) and '#' in tool_input:
            # Referansları ayıkla (ör. #E1, #E2)
            referenced_steps = re.findall(r'#(E\d+)', tool_input)
            resolved_data = []

            for ref in referenced_steps:
                if ref in results:
                    referenced_data = results[ref]

                    # Eğer önceki adımın sonucu bir liste ise (web_search gibi)
                    if isinstance(referenced_data, list):
                        if current_tool == "LLM":
                            # LLM aracı için snippet alanlarını al
                            resolved_data.extend(item['snippet'] for item in referenced_data)
                        elif current_tool == "parser":
                            # Parser aracı için link alanlarını al
                            resolved_data.extend(item['link'] for item in referenced_data)
                    elif isinstance(referenced_data, str):
                        resolved_data.append(referenced_data)

            # Eğer LLM düz metin bekliyorsa, birleştir ve döndür
            return " ".join(resolved_data) if current_tool == "LLM" else resolved_data

        elif isinstance(tool_input, list):
            # Eğer tool_input bir liste ise, her elemanı kontrol et
            parsed_links = [
                results[item[1:]] if item.startswith("#") and item[1:] in results else item
                for item in tool_input
            ]
            return parsed_links
        else:
            # tool_input düz metin ise, olduğu gibi döndür
            return tool_input

    @staticmethod
    async def _web_search(query):
        try:
            google_api_key = Config.GOOGLE_API_KEY
            search_engine_id = Config.SEARCH_ENGINE_ID
            if not google_api_key or not search_engine_id:
                raise ValueError("Google API key and Search Engine ID must be set.")
            search_url = f"https://www.googleapis.com/customsearch/v1?q={query}&key={google_api_key}&cx={search_engine_id}"
            response = requests.get(search_url)
            if response.status_code == 200:
                data = response.json()
                results = [{"link": item.get("link"), "snippet": item.get("snippet")} for item in data.get("items", [])]

                if results:
                    await UserNotificationService.notify_user(results=results)
                    await sleep(5)
                else:
                    logging.warning("There are no significant results to notify the users.")

                return results
            else:
                logging.error(f"Search API error: {response.status_code}")
                return [{"link": "", "snippet": f"Error: {response.status_code}"}]
        except Exception as e:
            logging.error(f"Web search failed: {e}")
            return [{"link": "", "snippet": "Error occurred during web search."}]

    @staticmethod
    async def _parser(input_data):
        """Verilen veri tipine göre uygun parser fonksiyonunu çağırır."""
        if isinstance(input_data, list):

            return ToolExecution._parser_list(input_data)
        elif isinstance(input_data, str):

            return ToolExecution._parser_url(input_data)
        elif isinstance(input_data, dict):

            return ToolExecution._parser_url(input_data["link"])
        else:
            logging.error("Input data is not in the expected format (list of dicts or str).")
            return "Input data must be a URL string or a list of dictionaries containing URLs."

    @staticmethod
    async def _parser_list(url_list):
        """URL içeren dictionary listesini işler."""
        parsed_results = []
        for item in url_list:
            url = item['link']

            if not ToolExecution._is_valid_url(url):
                logging.error(f"Invalid URL provided: {url}")
                return {
                    "title": "Invalid URL",
                    "content": "The provided input is not a valid URL."
                }

            if url:  # Eğer 'link' anahtarı varsa işle
                parsed_results.append(ToolExecution._parser_url(url))
            else:
                logging.warning("Item does not contain 'link' key.")
                parsed_results.append({
                    "url": None,
                    "title": "No URL",
                    "content": "Item does not contain a valid 'link' key."
                })
        return parsed_results

    @staticmethod
    async def _parser_url(url):
        """
        Tek bir URL'nin geçerli olup olmadığını kontrol eder, içeriğini alır,
        başlık ve ilk birkaç paragrafı çıkarır.
        """
        # URL doğrulama
        if not ToolExecution._is_valid_url(url):
            logging.error(f"Invalid URL provided: {url}")
            return {
                "title": "Invalid URL",
                "content": "The provided input is not a valid URL."
            }

        try:
            # User-Agent başlığı ekleniyor
            headers = {'User-Agent': Config.USER_AGENT}

            # Zaman aşımı kontrolü ile isteği gönder
            response = requests.get(url, headers=headers, timeout=10)

            # HTTP durumu kontrol et
            if response.status_code == 200:
                # İçerik tipi kontrolü
                content_type = response.headers.get('Content-Type', '')

                if 'text/html' not in content_type:
                    logging.warning(f"URL {url} returned non-HTML content: {content_type}")
                    return {
                        "title": "Unsupported Content",
                        "content": f"The content type '{content_type}' is not supported."
                    }

                # HTML içeriği işleme
                html_content = response.text
                soup = BeautifulSoup(html_content, "html.parser")

                # Sayfa başlığı
                title = soup.title.string.strip() if soup.title else "No Title"

                # İlk birkaç paragrafı al
                paragraphs = soup.find_all("p")
                if paragraphs:
                    content = "\n".join([p.get_text(strip=True) for p in paragraphs[:5]])
                else:
                    content = "No content found in paragraphs."

                return {
                    "title": title,
                    "content": content
                }
            else:
                logging.error(f"HTTP error for URL {url}: {response.status_code}")
                return {
                    "title": "Error",
                    "content": f"Error fetching URL content: HTTP {response.status_code}"
                }

        except requests.exceptions.Timeout:
            logging.error(f"Timeout occurred while trying to fetch {url}")
            return {
                "title": "Timeout Error",
                "content": "The request timed out while trying to fetch the URL."
            }

        except requests.exceptions.RequestException as e:
            logging.error(f"Request exception for URL {url}: {e}")
            return {
                "title": "Request Error",
                "content": f"An error occurred while making the request: {e}"
            }

        except Exception as e:
            logging.error(f"Parser failed for URL {url}: {e}")
            return {
                "title": "Parsing Error",
                "content": "An unexpected error occurred during parsing."
            }

    @staticmethod
    def _is_valid_url(url):
        """
        Gelen string'in geçerli bir URL olup olmadığını kontrol eder.
        """
        try:
            parsed = urlparse(url)
            # Scheme (örneğin, http veya https) ve netloc (örneğin, www.example.com) kontrolü yap
            return bool(parsed.scheme) and bool(parsed.netloc)
        except Exception as e:
            logging.error(f"Invalid URL: {url}: {e}")
            return False
