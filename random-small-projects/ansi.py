"""
ansi.py - ANSI escape code constants for use in terminal output.

Usage:
    from ansi import ANSI

    print(f"{ANSI.RED}Hello, World!{ANSI.RESET}")
    print(f"{ANSI.BOLD}{ANSI.BLUE}Bold Blue Text{ANSI.RESET}")
    print(f"{ANSI.BG_GREEN}{ANSI.BLACK}Black on Green{ANSI.RESET}")
"""


class ANSI:
    #* ── Main ───────────────────────────────────────────────────────────────
    RESET       = "\033[0m"
    NEW_LINE    = "\n"

    #* ── Text styles ────────────────────────────────────────────────────────
    BOLD        = "\033[1m"
    DIM         = "\033[2m"
    ITALIC      = "\033[3m"
    UNDERLINE   = "\033[4m"
    BLINK       = "\033[5m"
    INVERSE     = "\033[7m"
    HIDDEN      = "\033[8m"
    STRIKE      = "\033[9m"

    #* ── Foreground (text) colors ───────────────────────────────────────────
    BLACK       = "\033[30m"
    RED         = "\033[31m"
    GREEN       = "\033[32m"
    YELLOW      = "\033[33m"
    BLUE        = "\033[34m"
    MAGENTA     = "\033[35m"
    CYAN        = "\033[36m"
    WHITE       = "\033[37m"

    #* Bright variants
    BRIGHT_BLACK   = "\033[90m"
    BRIGHT_RED     = "\033[91m"
    BRIGHT_GREEN   = "\033[92m"
    BRIGHT_YELLOW  = "\033[93m"
    BRIGHT_BLUE    = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN    = "\033[96m"
    BRIGHT_WHITE   = "\033[97m"

    #* ── Background colors ──────────────────────────────────────────────────
    BG_BLACK    = "\033[40m"
    BG_RED      = "\033[41m"
    BG_GREEN    = "\033[42m"
    BG_YELLOW   = "\033[43m"
    BG_BLUE     = "\033[44m"
    BG_MAGENTA  = "\033[45m"
    BG_CYAN     = "\033[46m"
    BG_WHITE    = "\033[47m"

    #* Bright background variants
    BG_BRIGHT_BLACK   = "\033[100m"
    BG_BRIGHT_RED     = "\033[101m"
    BG_BRIGHT_GREEN   = "\033[102m"
    BG_BRIGHT_YELLOW  = "\033[103m"
    BG_BRIGHT_BLUE    = "\033[104m"
    BG_BRIGHT_MAGENTA = "\033[105m"
    BG_BRIGHT_CYAN    = "\033[106m"
    BG_BRIGHT_WHITE   = "\033[107m"

    #* ── Helper methods ─────────────────────────────────────────────────────
    @staticmethod
    def rgb(r: int, g: int, b: int) -> str:
        """True-color (24-bit) foreground: ANSI.rgb(255, 128, 0)"""
        return f"\033[38;2;{r};{g};{b}m"

    @staticmethod
    def bg_rgb(r: int, g: int, b: int) -> str:
        """True-color (24-bit) background: ANSI.bg_rgb(0, 0, 128)"""
        return f"\033[48;2;{r};{g};{b}m"

    @staticmethod
    def color256(n: int) -> str:
        """256-color foreground (0-255): ANSI.color256(214)"""
        return f"\033[38;5;{n}m"

    @staticmethod
    def bg_color256(n: int) -> str:
        """256-color background (0-255): ANSI.bg_color256(214)"""
        return f"\033[48;5;{n}m"

    @staticmethod
    def wrap(text: str, *codes: str) -> str:
        """Wrap text with one or more ANSI codes and auto-reset at the end.

        Example:
            print(ANSI.wrap("Hello!", ANSI.BOLD, ANSI.RED))
        """
        return "".join(codes) + text + ANSI.RESET


#* ── Quick demo ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print(f"{ANSI.RED}Red text{ANSI.RESET}")
    print(f"{ANSI.BOLD}{ANSI.BLUE}Bold blue{ANSI.RESET}")
    print(f"{ANSI.BG_YELLOW}{ANSI.BLACK}Black on yellow{ANSI.RESET}")
    print(f"{ANSI.UNDERLINE}{ANSI.GREEN}Underlined green{ANSI.RESET}")
    print(ANSI.wrap("Wrapped magenta + bold", ANSI.MAGENTA, ANSI.BOLD))
    print(ANSI.rgb(255, 128, 0) + "True-color orange" + ANSI.RESET)
    print(ANSI.color256(214) + "256-color orange" + ANSI.RESET)