# Utils/math_utils.py
import re
from typing import Dict, Any


class MathDetector:
    """
    Detects and quantifies mathematical density in scientific text.
    Useful for identifying theoretical vs empirical papers.
    """
    # Raw strings eliminate redundant escape warnings
    INLINE_MATH = re.compile(r"\$[^\$]+\$")
    DISPLAY_MATH = re.compile(r"\$\$.*?\$\$|\\\[.*?\\\]", re.DOTALL)
    EQUATION_ENV = re.compile(r"\\begin\{equation\*?\}.*?\\end\{equation\*?\}", re.DOTALL)
    COMMON_SYMBOLS = re.compile(r"\\[a-zA-Z]+|\{.*?\}|_|\^")

    @staticmethod
    def analyze(text: str) -> Dict[str, Any]:
        inline_count = len(MathDetector.INLINE_MATH.findall(text))
        display_count = len(MathDetector.DISPLAY_MATH.findall(text)) + len(MathDetector.EQUATION_ENV.findall(text))
        symbol_density = len(MathDetector.COMMON_SYMBOLS.findall(text)) / max(len(text.split()), 1)

        total_equations = inline_count + display_count
        math_density_score = min(1.0, (total_equations / 50.0) + (symbol_density / 5.0))

        return {
            "inline_math_count": inline_count,
            "display_math_count": display_count,
            "total_equations": total_equations,
            "symbol_density": round(symbol_density, 4),
            "math_density_score": round(math_density_score, 4),
            "is_theory_heavy": math_density_score > 0.5,
        }