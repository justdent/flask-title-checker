import pandas as pd
from Levenshtein import ratio
import os
import re
from typing import List, Dict
from collections import Counter

class ExcelTitleChecker:
    def __init__(self, excel_paths: List[str], prefixes: List[str], suffixes: List[str], disallowed_words: List[str]):
        self.excel_paths = excel_paths
        self.disallowed_words = disallowed_words
        self.common_prefixes = prefixes
        self.common_suffixes = suffixes
        self.titles_db = self._load_databases()

    def _load_databases(self) -> pd.DataFrame:
        """Load and combine all Excel databases, supporting multiple sheets."""
        all_titles = []

        for path in self.excel_paths:
            try:
                file_ext = os.path.splitext(path)[1].lower()
                if file_ext == ".xls":
                    df = pd.read_excel(path, engine='xlrd', sheet_name=None)
                else:
                    df = pd.read_excel(path, sheet_name=None)

                for sheet_name, sheet_data in df.items():
                    sheet_data.columns = sheet_data.columns.str.lower()
                    possible_title_cols = ['title', 'title name', 'titlename']
                    matched_title_col = next((col for col in sheet_data.columns if col in possible_title_cols), None)

                    if matched_title_col:
                        sheet_data = sheet_data[[matched_title_col]].rename(columns={matched_title_col: 'title'})
                        sheet_data['source'] = f"{os.path.basename(path)} - {sheet_name}"
                        all_titles.append(sheet_data)
                    else:
                        print(f"❌ '{path}' - Sheet '{sheet_name}' skipped: no recognized title column.")
            except Exception as e:
                print(f"❌ Error loading '{path}': {str(e)}")

        if not all_titles:
            raise ValueError("No valid Excel files with a title column found.")

        return pd.concat(all_titles, ignore_index=True)

    def check_disallowed_words(self, input_title: str) -> List[str]:
        """Check for disallowed words with whole word matching."""
        found_words = []
        input_title_lower = input_title.lower().strip()
        for word in self.disallowed_words:
            if re.search(r'\b' + re.escape(word.lower()) + r'\b', input_title_lower):
                found_words.append(word)
        return found_words

    def check_common_patterns(self, input_title: str) -> List[Dict]:
        """Detect and count known prefixes/suffixes in words of the title."""
        input_title_lower = input_title.lower().strip()
        words = input_title_lower.split()

        prefix_matches = []
        suffix_matches = []

        for word in words:
            for prefix in self.common_prefixes:
                if word.startswith(prefix):
                    prefix_matches.append(prefix)
            for suffix in self.common_suffixes:
                if word.endswith(suffix):
                    suffix_matches.append(suffix)

        patterns = []
        for prefix, count in Counter(prefix_matches).items():
            patterns.append({"type": "prefix", "text": prefix, "count": count})
        for suffix, count in Counter(suffix_matches).items():
            patterns.append({"type": "suffix", "text": suffix, "count": count})

        return patterns

    def check_similarity(self, input_title: str) -> Dict:
        """Check similarity against all titles in the database."""
        input_title = input_title.lower().strip()
        max_similarity = 0
        best_match = ""
        best_source = ""

        for _, row in self.titles_db.iterrows():
            db_title = row['title'].lower().strip()
            current_similarity = ratio(input_title, db_title)

            if current_similarity > max_similarity:
                max_similarity = current_similarity
                best_match = row['title']
                best_source = row['source']

        found_words = self.check_disallowed_words(input_title)
        patterns = self.check_common_patterns(input_title)

        return {
            'similarity_score': round(max_similarity * 100, 2),
            'matched_title': best_match if max_similarity > 0.3 else None,
            'matched_source': best_source if max_similarity > 0.3 else None,
            'disallowed_words': found_words,
            'common_patterns': patterns
        }
