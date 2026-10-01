# Credits & third-party licenses

## Installed on request (not bundled - fetched from the official repos by `install.sh`)
| | license | source |
|---|---|---|
| **ui-ux-pro-max** - UI/UX design intelligence | MIT | https://github.com/nextlevelbuilder/ui-ux-pro-max-skill |
| **caveman** - shorter, token-cheap Claude answers | Apache-2.0 ("Caveman" is a trademark of Julius Brussee; this project is not affiliated) | https://github.com/JuliusBrussee/caveman |

## Downloaded at first use (not bundled)
| | license | note |
|---|---|---|
| **Noto Color Emoji** (non-Mac systems) | SIL OFL 1.1 | https://github.com/googlefonts/noto-emoji |
| **rembg** + u2net_human_seg model (non-Mac background removal) | MIT / Apache-2.0 | https://github.com/danielgatis/rembg |
| **MMS_FA forced-alignment model** (Meta, via torchaudio) | **CC-BY-NC 4.0 - non-commercial** | Used to time words to the audio when captions aren't in Latin letters or the Gemini transcriber is used. Check the license before using it for paid/commercial work. |

## Bundled assets
| | license | source |
|---|---|---|
| Microsoft Fluent 3D emoji (`reel-dark/template/assets/icons/fluent`) | MIT | https://github.com/microsoft/fluentui-emoji |
| Inter, Noto Sans Arabic, JetBrains Mono, Source Serif 4 (`reel-dark/template/assets/fonts`, OFL texts included) | SIL OFL 1.1 | Google Fonts |
| Montserrat font (`reel-white/assets/fonts`) | SIL OFL 1.1 | https://fonts.google.com/specimen/Montserrat |
| Sound effects (`reel-dark/template/audio`) | MIT (synthesized by `make_sfx.py` in this repo) | this repo |
| Brand logos and app icons (Claude, Meta, Instagram, OpenAI, GitHub, WhatsApp, …) | trademarks of their owners | used only to depict those products in demo screens (nominative use) |

## Uses at runtime from the user's system
On macOS: Apple SF Pro / SF Arabic / New York fonts, Apple Color Emoji and the Vision framework (never redistributed);
ffmpeg; hyperframes (npx, white style); Fish Audio and OpenRouter APIs with the user's own keys.
