"""Inline markup shared by both renderers.

The authored text uses a deliberately tiny subset of Markdown so that the same
string can go to HTML and to LaTeX without a real parser:

    **bold**   *italic*   `code`   ==mark==   [label](href)   --  (en dash)

Everything else is literal. Keeping the subset this small is what lets the two
renderers stay in agreement; anything richer belongs in a typed block instead.
"""

import re

_LINK = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
_BOLD = re.compile(r"\*\*(.+?)\*\*", re.S)
_ITAL = re.compile(r"(?<!\*)\*([^*]+?)\*(?!\*)")
_CODE = re.compile(r"`([^`]+?)`")
_MARK = re.compile(r"==(.+?)==", re.S)


# ---------------------------------------------------------------- HTML --------

_HTML_ESC = {"&": "&amp;", "<": "&lt;", ">": "&gt;"}


def esc_html(s):
    return "".join(_HTML_ESC.get(c, c) for c in str(s))


def html(s):
    """Inline markup -> HTML. Escapes first, so authored text cannot inject tags."""
    if s is None:
        return ""
    out = esc_html(s)
    # placeholders keep link hrefs away from the emphasis passes
    links = []

    def stash(m):
        links.append((m.group(1), m.group(2)))
        return f"\x00L{len(links) - 1}\x00"

    out = _LINK.sub(stash, out)
    out = _CODE.sub(lambda m: f'<code class="inline">{m.group(1)}</code>', out)
    out = _BOLD.sub(lambda m: f"<b>{m.group(1)}</b>", out)
    out = _ITAL.sub(lambda m: f"<i>{m.group(1)}</i>", out)
    out = _MARK.sub(lambda m: f'<span class="sig-text">{m.group(1)}</span>', out)
    out = out.replace("--", "&ndash;")
    for i, (label, href) in enumerate(links):
        out = out.replace(
            f"\x00L{i}\x00",
            f'<a href="{href}" target="_blank" rel="noopener">{label}</a>')
    return out


# --------------------------------------------------------------- LaTeX --------

_TEX_ESC = [
    ("\\", r"\textbackslash{}"),
    ("&", r"\&"), ("%", r"\%"), ("$", r"\$"), ("#", r"\#"),
    ("_", r"\_"), ("{", r"\{"), ("}", r"\}"),
    ("~", r"\textasciitilde{}"), ("^", r"\textasciicircum{}"),
]

# Characters that turn up in the book text and have no place in pdfLaTeX's
# default encoding. Mapped rather than escaped.
_TEX_CHARS = {
    "—": "---", "–": "--", "‑": "-", "−": "$-$",
    "“": "``", "”": "''", "‘": "`", "’": "'",
    "…": r"\ldots{}", "×": r"$\times$", "→": r"$\rightarrow$",
    "←": r"$\leftarrow$", "≈": r"$\approx$", "≤": r"$\leq$", "≥": r"$\geq$",
    "≠": r"$\neq$", "±": r"$\pm$", "·": r"$\cdot$", "°": r"$^\circ$",
    "√": r"$\sqrt{}$", "∈": r"$\in$", "∀": r"$\forall$", "∑": r"$\sum$",
    "⊂": r"$\subset$", "⊃": r"$\supset$", "⊆": r"$\subseteq$",
    "⊇": r"$\supseteq$", "∪": r"$\cup$", "∩": r"$\cap$", "∅": r"$\emptyset$",
    "∃": r"$\exists$", "∄": r"$\nexists$", "∧": r"$\wedge$", "∨": r"$\vee$",
    "¬": r"$\neg$", "≡": r"$\equiv$", "∞": r"$\infty$", "∝": r"$\propto$",
    "∫": r"$\int$", "∏": r"$\prod$", "⇒": r"$\Rightarrow$",
    "⇔": r"$\Leftrightarrow$", "↦": r"$\mapsto$", "↑": r"$\uparrow$",
    "↓": r"$\downarrow$", "⌈": r"$\lceil$", "⌉": r"$\rceil$",
    "⌊": r"$\lfloor$", "⌋": r"$\rfloor$", "⟨": r"$\langle$", "⟩": r"$\rangle$",
    "‖": r"$\|$", "⊤": r"$\top$", "⊥": r"$\perp$", "′": r"$\prime$",
    "•": r"\textbullet{}", "▪": r"\textbullet{}", "→": r"$\rightarrow$",
    "Δ": r"$\Delta$", "Σ": r"$\Sigma$", "Π": r"$\Pi$", "Ω": r"$\Omega$",
    "Φ": r"$\Phi$", "Ψ": r"$\Psi$", "Γ": r"$\Gamma$", "Λ": r"$\Lambda$",
    "ω": r"$\omega$", "ρ": r"$\rho$", "τ": r"$\tau$", "φ": r"$\varphi$",
    "χ": r"$\chi$", "ψ": r"$\psi$", "η": r"$\eta$", "ζ": r"$\zeta$",
    "κ": r"$\kappa$", "ν": r"$\nu$", "ξ": r"$\xi$", "υ": r"$\upsilon$",
    "⁰": r"$^{0}$", "¹": r"$^{1}$", "²": r"$^{2}$", "³": r"$^{3}$",
    "⁴": r"$^{4}$", "⁵": r"$^{5}$", "⁶": r"$^{6}$", "⁷": r"$^{7}$",
    "⁸": r"$^{8}$", "⁹": r"$^{9}$", "⁻": r"$^{-}$", "ⁿ": r"$^{n}$",
    "₀": r"$_{0}$", "₁": r"$_{1}$", "₂": r"$_{2}$", "₃": r"$_{3}$",
    "≪": r"$\ll$", "≫": r"$\gg$", "√": r"$\sqrt{}$",
    "∇": r"$\nabla$", "∂": r"$\partial$", "α": r"$\alpha$", "β": r"$\beta$",
    "γ": r"$\gamma$", "δ": r"$\delta$", "ε": r"$\varepsilon$", "θ": r"$\theta$",
    "λ": r"$\lambda$", "μ": r"$\mu$", "σ": r"$\sigma$", "π": r"$\pi$",
    "ℓ": r"$\ell$", "ƒ": "f", "™": r"\texttrademark{}", "©": r"\textcopyright{}",
    " ": "~", "​": "",
}


def esc_tex(s):
    """Escape TeX specials, then map the unicode we actually use.

    Order matters: the unicode replacements emit backslashes and braces of
    their own, so they have to land *after* the generic escaping pass or they
    get escaped a second time (``≈`` came out as ``\\$\\textbackslash...``).
    """
    s = str(s)
    for ch, rep in _TEX_ESC:
        s = s.replace(ch, rep)
    for ch, rep in _TEX_CHARS.items():
        s = s.replace(ch, rep)
    return s


def tex_url(u):
    """Escape a URL for hyperref's first argument.

    ``#`` ``%`` ``&`` ``_`` are all legal in URLs and all special to TeX, so they
    have to be escaped here rather than run through ``esc_tex`` (which would
    also mangle the slashes and tildes)."""
    out = str(u)
    for ch in ("\\", "#", "%", "&", "_", "{", "}"):
        out = out.replace(ch, "\\" + ch)
    return out.replace("~", r"\textasciitilde{}")


def tex(s):
    """Inline markup -> LaTeX."""
    if s is None:
        return ""
    stash = []

    def keep(rep):
        stash.append(rep)
        return f"\x00S{len(stash) - 1}\x00"

    # Pull verbatim-ish and link pieces out BEFORE escaping, so their payload
    # is escaped by the rule that suits it rather than the generic one.
    src = str(s)
    src = _LINK.sub(lambda m: keep(r"\hlink{%s}{%s}" % (tex_url(m.group(2)),
                                                        esc_tex(m.group(1)))), src)
    src = _CODE.sub(lambda m: keep(r"\inlinecode{%s}" % esc_tex(m.group(1))), src)

    out = esc_tex(src)
    out = _BOLD.sub(lambda m: r"\textbf{%s}" % m.group(1), out)
    out = _ITAL.sub(lambda m: r"\textit{%s}" % m.group(1), out)
    out = _MARK.sub(lambda m: r"\hilite{%s}" % m.group(1), out)
    for i, rep in enumerate(stash):
        out = out.replace(f"\x00S{i}\x00", rep)
    return out
