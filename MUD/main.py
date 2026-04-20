from utils import cprint, cstrip


if __name__ == "__main__":
    samples = [
        "&+cAshenmoor&N -- a text adventure",
        "&Rwarning:&N health is &+Rcritically low&N!",
        "&+WTHE RUSTY FLAGON&N",
        "&WPlatinum&N: 152 &YGold&N: 42  &wSilver&N: 7  &yCopper&N: 3",
        "&ggreen&N  &+Gbright green&N  &ccyan&N  &+cbright cyan&N",
        "&mmagenta&N  &Mbright magenta&N  &bblue&N  &Bbright blue&N",
        "&&N is a literal ampersand-N, not a reset",
    ]
    print("\n\033[1m-- terminal ANSI demo --\033[0m")
    for s in samples:
        print(f"  raw: {s}")
        cprint(f"  out: {s}")
        print()
    print("\033[1m-- cstrip --\033[0m")
    for s in samples:
        print(f"  {cstrip(s)}")
