import os
class DownloadPapers:
    def create_project_files(self, QUERY, HITS, OUTPUT):
        os.system(f'pygetpapers -q "{QUERY}" -k {HITS} -o {OUTPUT} -x')
        os.system(f"ami -p {OUTPUT} section")