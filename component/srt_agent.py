import os
import re
from typing import Dict, List, Tuple
from datetime import timedelta

from langchain.schema import HumanMessage, SystemMessage

from component.response import llm

class Subtitle:
    def __init__(self, index: int, start: timedelta, end: timedelta, text: str):
        self.index = index
        self.start = start
        self.end = end
        self.text = text

    def __str__(self):
        return f"{self.index}\n{self.start} --> {self.end}\n{self.text}"

class ImprovedSRTAgent:
    def __init__(self, directory: str):
        self.srt_files: Dict[str, List[Subtitle]] = {}
        self.load_srt_files(directory)
        self.llm = llm

    def load_srt_files(self, directory: str):
        for filename in os.listdir(directory):
            if filename.endswith('.srt'):
                file_path = os.path.join(directory, filename)
                try:
                    with open(file_path, 'r', encoding='utf-8-sig') as file:
                        content = file.read()
                    self.srt_files[filename] = self.parse_srt(content)
                except Exception as e:
                    print(f"Error parsing {filename}: {e}")

    def parse_srt(self, content: str) -> List[Subtitle]:
        pattern = r'(\d+)\n(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})\n((?:.*\n)*?)\n'
        matches = re.findall(pattern, content, re.MULTILINE)
        
        subtitles = []
        for match in matches:
            index = int(match[0])
            start = self.parse_time(match[1])
            end = self.parse_time(match[2])
            text = match[3].strip()
            subtitles.append(Subtitle(index, start, end, text))
        
        return subtitles

    def parse_time(self, time_str: str) -> timedelta:
        hours, minutes, seconds = time_str.replace(',', '.').split(':')
        return timedelta(hours=int(hours), minutes=int(minutes), seconds=float(seconds))

    def get_subtitle_at_time(self, filename: str, time: str) -> str:
        if filename not in self.srt_files:
            return f"File {filename} not found."
        
        target_time = self.parse_time(time)
        for subtitle in self.srt_files[filename]:
            if subtitle.start <= target_time < subtitle.end:
                return subtitle.text
        
        return "No subtitle found at the specified time."

    def search_subtitles(self, filename: str, keyword: str) -> List[str]:
        if filename not in self.srt_files:
            return [f"File {filename} not found."]
        
        results = []
        for subtitle in self.srt_files[filename]:
            if keyword.lower() in subtitle.text.lower():
                results.append(f"{subtitle.start} - {subtitle.end}: {subtitle.text}")
        
        return results if results else ["No matches found."]

    def list_files(self) -> List[str]:
        return list(self.srt_files.keys())

    def get_file_info(self, filename: str) -> str:
        if filename not in self.srt_files:
            return f"File {filename} not found."
        
        subtitles = self.srt_files[filename]
        duration = subtitles[-1].end
        content_preview = "\n".join([sub.text for sub in subtitles[:3]])
        return f"File: {filename}\nNumber of subtitles: {len(subtitles)}\nDuration: {duration}\nContent preview:\n{content_preview}"

    def get_full_content(self, filename: str) -> str:
        if filename not in self.srt_files:
            return f"File {filename} not found."
        
        return "\n".join([sub.text for sub in self.srt_files[filename]])

    def query(self, user_query: str) -> str:
        system_message = SystemMessage(content="""You are an AI assistant specializing in SRT (SubRip Subtitle) file analysis. 
        You can provide detailed information about SRT files, including their content, number of subtitles, and duration. 
        Use the provided information to answer the user's query accurately and comprehensively.""")

        context = f"Available SRT files: {', '.join(self.list_files())}\n\n"
        context += "File Information:\n"
        for filename in self.srt_files:
            context += f"{self.get_file_info(filename)}\n\n"

        human_message = HumanMessage(content=f"{context}\nQuery: {user_query}")

        response = self.llm([system_message, human_message])
        return response.content

# Example usage
# if __name__ == "__main__":
#     directory = r"D:\projects\VS_code\internships\smartcard_python\test_uploads\srt_data"
#     agent = ImprovedSRTAgent(directory)

#     query = "What is sample.srt about?"
#     result = agent.query(query)
#     print(f"Query: {query}")
#     print(f"Result: {result}")