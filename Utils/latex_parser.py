# Utils/latex_parser.py
import re


def strip_latex(text: str) -> str:
    """
    Lightweight LaTeX cleaner for arXiv-style papers.
    Removes common commands, environments, and math markup while preserving readability.
    """
    if not text.strip():
        return ""

    # Remove comments
    text = re.sub(r"%.*$", "", text, flags=re.MULTILINE)

    # Remove common environments (keep content)
    env_patterns = [
        r"\\begin\{abstract\}(.*?)\\end\{abstract\}",
        r"\\begin\{document\}(.*?)\\end\{document\}",
        r"\\begin\{figure\}.*?\\end\{figure\}",
        r"\\begin\{table\}.*?\\end\{table\}",
    ]
    for pat in env_patterns:
        text = re.sub(pat, r"\1", text, flags=re.DOTALL)

    # Remove \section{...}, \subsection{...}
    text = re.sub(r"\\(?:section|subsection|subsubsection)\{([^}]*)\}", r"\1", text)

    # Remove \cite{...}, \ref{...}, \label{...}
    text = re.sub(r"\\(?:cite|ref|label|eqref)\{[^}]*\}", "", text)

    # Remove \textbf{...}, \textit{...}, \emph{...}
    # Intentional LaTeX commands — suppress typo warnings
    # noinspection SpellCheckingInspection
    text = re.sub(r"\\(?:textbf|textit|emph)\{([^}]*)\}", r"\1", text)

    # Remove inline math $...$
    text = re.sub(r"\$[^\$]*\$", " [MATH] ", text)

    # Remove display math $$...$$ or \[ ... \]
    text = re.sub(r"\$\$.*?\$\$", " [DISPLAY MATH] ", text, flags=re.DOTALL)
    text = re.sub(r"\\\[.*?\\\]", " [DISPLAY MATH] ", text, flags=re.DOTALL)

    # Remove common commands (with typo suppression)
    # noinspection SpellCheckingInspection
    commands_to_remove = [
        r"\\title\{.*?\}",
        r"\\author\{.*?\}",
        r"\\maketitle",
        r"\\usepackage\{.*?\}",
        r"\\documentclass\[.*?\]\{.*?\}",
        r"\\begin\{.*?\}",
        r"\\end\{.*?\}",
    ]
    for cmd in commands_to_remove:
        text = re.sub(cmd, "", text, flags=re.DOTALL)

    # Clean up excessive whitespace
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]+", " ", text)

    return text.strip()