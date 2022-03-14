from pathlib import Path


class Xterm256Colors:
    BASIC16 = (
        (0, 0, 0),
        (128, 0, 0),
        (0, 128, 0),
        (128, 128, 0),
        (0, 0, 238),
        (128, 0, 128),
        (0, 128, 128),
        (192, 192, 192),
        (128, 128, 128),
        (255, 0, 0),
        (0, 255, 0),
        (255, 255, 0),
        (0, 0, 255),
        (255, 0, 255),
        (0, 255, 255),
        (255, 255, 255),
    )
    CUBE_STEPS = (0x00, 0x5F, 0x87, 0xAF, 0xD7, 0xFF)

    def __getitem__(self, n_color):
        """Convert xterm color index to corresponding RGB triplet.

        Parameters
        ----------
        n_color : int
            Index of xterm color.

        References
        ----------
        https://github.com/jart/fabulous/blob/19903cf0a980b82f5928c3bec1f28b6bdd3785bd/fabulous/xterm256.py
        https://www.ditig.com/256-colors-cheat-sheet
        """
        assert 0 <= n_color <= 255

        if n_color < 16:
            return self.BASIC16[n_color]
        elif 16 <= n_color <= 231:
            # color cube
            n_color -= 16
            return (
                self.CUBE_STEPS[n_color // 36 % 6],
                self.CUBE_STEPS[n_color // 6 % 6],
                self.CUBE_STEPS[n_color % 6],
            )
        elif 232 <= n_color <= 255:
            # gray tone
            c = 8 + (n_color - 232) * 0x0A
            return (c, c, c)

    def __iter__(self):
        return (self[i] for i in range(256))

    @property
    def save_dir(self):
        return Path("./imgs/")

    def save_name(self, rgb):
        return self.triplet2hex(rgb)[1:]

    def save_svg(self):
        self.save_dir.mkdir(exist_ok=True)

        for rgb in iter(self):
            bg_hex = self.triplet2hex(rgb)
            fg_hex = self.triplet2hex(self.adaptive_fg_color(rgb))

            svg_path = self.save_dir / f"{self.save_name(rgb)}.svg"
            with open(svg_path, "w") as f:
                f.write(
                    f"""<svg xmlns="http://www.w3.org/2000/svg" width="600" height="40">
    <rect x="0" y="0" width="600" height="40" fill="{bg_hex}"/>
    <text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle" font-size="20" fill="{fg_hex}">{rgb}</text>
</svg>
"""
                )

    @staticmethod
    def triplet2hex(rgb):
        """
        Convert RGB triplet to hexadecimal color.
        """
        assert all(0 <= c <= 255 and isinstance(c, int) for c in rgb)
        r, g, b = rgb
        return f"#{r:02x}{g:02x}{b:02x}"

    @staticmethod
    def adaptive_fg_color(bg):
        """
        Return contrastive foreground color based on background color.

        Parameters
        ----------
        bg : Tuple[int]
            Background color of RGB triplet format.
        """
        assert all(0 <= c <= 255 and isinstance(c, int) for c in bg)

        offset = 96
        if max(bg) > 255 - offset:
            offset *= -1

        return tuple(min(255, max(0, c + offset)) for c in bg)

    def generate_readme(self):
        with open("README.md", "w") as f:
            f.write(
                f"""<table align="center" border="0">
<tr>
<td align="center"><b>Index</b></td>
<td align="center"><b>Hex</b></td>
<td align="center"><b>Display</b></td>
</tr>
"""
            )
            for i, rgb in enumerate(self):
                hex_color = self.triplet2hex(rgb)
                svg_path = self.save_dir / f"{self.save_name(rgb)}.svg"
                f.write(
                    f"""<tr>
<td align="center">{i}</td>
<td align="center">

#### `{hex_color}`
</td>
<td align="center"><img src="{svg_path}"></td>
</tr>
"""
                )
            f.write("</table>\n")


if __name__ == "__main__":
    colors = Xterm256Colors()
    colors.save_svg()
    colors.generate_readme()
