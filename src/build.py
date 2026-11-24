"""
Gera o site da Dra. Melina Corradi (cirurgiã-dentista, Mateus Leme, MG) em dist/.

Cada página de src/pages começa com um comentário de metadados:
<!--meta {"title": "...", "description": "...", "nav": "sobre"} -->

Marcadores disponíveis dentro das páginas:
  {{ARROW}} {{ICON:nome}}  seta e ícones
  {{WA}} {{WA_FONE}}       link e telefone do WhatsApp
  {{IG}} {{ENDERECO}}      Instagram e endereço
  {{ROTA}} {{MAPA}}        rota e mapa do Google
  {{RAIL}}                 vitrine de vídeos
  {{REEL:id}}              um vídeo solto
  {{TRAT_GRID}}            grade de tratamentos (home)
  {{TRAT_FULL}}            tratamentos detalhados (página Tratamentos)
  {{EQUIPE}}               cartões da equipe
  {{PASSOS}}               passo a passo da consulta
  {{FAQ}}                  perguntas frequentes
  {{COMPARE}}              antes e depois arrastável
  {{POSTS}}                mosaico de posts e casos do Instagram
  {{FORM}}                 formulário de agendamento que vai para o WhatsApp

Uso:  python src/build.py
"""
import json
import pathlib
import re
from html import escape
from urllib.parse import quote, quote_plus

ROOT = pathlib.Path(__file__).resolve().parent.parent
PAGES = ROOT / "src" / "pages"
OUT = ROOT / "dist"
SITE = "https://melinacorradi.achillesmedia.com.br"
V = "1"  # versão dos arquivos estáticos; aumente a cada publicação de CSS ou JS

# ------------------------------------------------------------------
# Dados. Altere aqui e rode o build de novo.
# ------------------------------------------------------------------
PERFIL = {
    "nome": "Dra. Melina Corradi",
    "cro": "CRO-MG 47295",
    "wa": "553197801670",          # link da bio do Instagram (wa.me/3197801670)
    "wa_fone": "(31) 99780-1670",
    "instagram": "https://www.instagram.com/dra.mellcorr/",
    "rua": "Avenida Getúlio Vargas, 523",
    "bairro": "Centro",
    "cidade": "Mateus Leme, MG",
    "horario": "Segunda a sábado, com hora marcada",
}
PERFIL["q"] = f"{PERFIL['rua']}, {PERFIL['bairro']}, {PERFIL['cidade']}"
WA_MSG = "Olá, Dra. Melina! Vim pelo site e gostaria de agendar uma avaliação."

NAV = [  # (chave, rótulo, arquivo, aparece no topo)
    ("index", "Início", "index.html", False),
    ("sobre", "A doutora", "sobre.html", True),
    ("tratamentos", "Tratamentos", "tratamentos.html", True),
    ("resultados", "Resultados", "resultados.html", True),
    ("clinica", "Clínica e equipe", "clinica.html", True),
    ("agendamento", "Agendamento", "agendamento.html", True),
    ("contato", "Contato", "contato.html", True),
]

# Vídeos do Instagram dela. id = código do post; textos curtos escritos a partir das legendas.
REELS = [
    ("DfYAXrGz4VZ", "Clareamento", "Sorriso de fim de ano", "O sorriso branco das fotos de fim de ano começa agora, no consultório."),
    ("DeznLfhzDHL", "Prótese", "Prótese total caracterizada", "Naturalidade nos detalhes: a caracterização deixa a prótese com cara de sorriso de verdade."),
    ("Da5pksku9-i", "A clínica", "Como chegar", "Do centro de Mateus Leme até a recepção: um passeio pela clínica."),
    ("DaQxkYHPgCk", "Bastidores", "Excelência em cada detalhe", "Atendimento humanizado, tecnologia e cuidado em cada consulta."),
    ("DfXwjb7TOo5", "Clareamento", "Na cadeira", "Clareamento de consultório com luz e acompanhamento da doutora."),
    ("DfpK3YQz5Sw", "Ortodontia", "Manutenção do aparelho", "A dúvida de todo paciente na hora de escolher a cor das borrachinhas."),
    ("DagDDjMzj0t", "Estética", "O sorriso dos seus sonhos", "Planejamento para um resultado bonito, natural e duradouro."),
    ("DaiCMiSTL7n", "Compromisso", "Diagnóstico honesto", "Seu sorriso merece respeito: cada diagnóstico é feito com transparência."),
    ("DaYDmyMuWdY", "Prevenção", "Fio dental todo dia", "A escova limpa o que está à vista; o fio chega onde ela não alcança."),
    ("Db6jGPLPTpu", "Avaliação", "Agende sua avaliação", "Instrumentais prontos para a sua consulta no consultório particular."),
    ("DasonEkuOTm", "Bastidores", "Ela não desiste", "Bom humor e determinação: a rotina de quem ama o que faz."),
    ("Dax0mEfuKVJ", "Clareamento", "Clarea Day", "Uma paciente conta como foi o clareamento na semana especial."),
    ("DbBME_muqbY", "Clareamento", "Semana do Clarea Day", "Condições especiais para quem queria um sorriso mais branco."),
    ("Ddjnja_Tqda", "Bastidores", "Chamem a dentista", "Por aqui o atendimento é sério, mas a diversão também faz parte."),
]
REEL = {r[0]: r for r in REELS}
DESTAQUE = ["DfYAXrGz4VZ", "DeznLfhzDHL", "DaQxkYHPgCk", "DfXwjb7TOo5", "DfpK3YQz5Sw", "DagDDjMzj0t", "Da5pksku9-i",
            "DaiCMiSTL7n", "DaYDmyMuWdY", "Db6jGPLPTpu"]

TRATAMENTOS = [
    {"id": "clareamento", "nome": "Clareamento dental", "icon": "sparkle", "img": "img/fotos/clareamento.jpg",
     "curto": "Consultório, caseiro supervisionado ou combinado, sempre após avaliação.",
     "texto": "O clareamento começa com uma avaliação e uma limpeza. Depois a doutora indica o protocolo certo: sessões no consultório, moldeiras personalizadas para usar em casa ou a combinação dos dois.",
     "itens": ["Clareamento de consultório", "Caseiro com moldeiras personalizadas", "Protocolo combinado", "Profilaxia antes do tratamento"]},
    {"id": "implantes", "nome": "Implantes dentários", "icon": "implant", "img": "img/fotos/implante-caso.jpg",
     "curto": "Reabilitação de dentes perdidos com planejamento individual.",
     "texto": "A falta de um dente compromete a mastigação, a fala e até a posição dos vizinhos. Com planejamento e técnica, em muitos casos o novo sorriso fica pronto em cerca de 90 dias.",
     "itens": ["Avaliação com radiografia", "Implante unitário ou múltiplo", "Prótese sobre implante", "Acompanhamento da cicatrização"]},
    {"id": "proteses", "nome": "Próteses e coroas", "icon": "tooth", "img": "img/fotos/protese.jpg",
     "curto": "Prótese total caracterizada e coroas que devolvem função e estética.",
     "texto": "A Dra. Melina é protesista. Próteses totais com caracterização de gengiva e dentes, coroas totais e reabilitações que devolvem conforto para mastigar e segurança para sorrir.",
     "itens": ["Prótese total removível caracterizada", "Coroa total", "Prótese sobre implante", "Ajustes e manutenção"]},
    {"id": "ortodontia", "nome": "Ortodontia", "icon": "braces", "img": "img/fotos/aparelho-estetico.jpg",
     "curto": "Aparelho convencional, estético, autoligado ou alinhadores invisíveis.",
     "texto": "Ortodontia não é só estética: é função. Com o Dr. Franklin Araújo, ortodontista e ortopedista facial, você conhece as opções e descobre qual é a mais indicada para o seu caso.",
     "itens": ["Aparelho convencional", "Aparelho estético de cerâmica", "Aparelho autoligado", "Alinhadores invisíveis"]},
    {"id": "limpeza", "nome": "Limpeza e prevenção", "icon": "shield", "img": "img/fotos/limpeza-post.jpg",
     "curto": "Profilaxia profissional que remove placa, tártaro e manchas.",
     "texto": "Mesmo com boa escovação, a placa endurece e vira tártaro onde a escova não chega. A limpeza profissional previne gengivite, cárie e mau hálito, e consultas regulares evitam tratamentos maiores.",
     "itens": ["Profilaxia e remoção de tártaro", "Orientação de higiene", "Prevenção de cárie e gengivite", "Retornos programados"]},
    {"id": "restauracoes", "nome": "Restaurações", "icon": "drop", "img": "img/fotos/coroa.jpg",
     "curto": "Resina composta na cor do dente e cuidado com a polpa.",
     "texto": "Restaurações em resina que imitam a cor e o brilho do dente natural, inclusive em casos profundos com capeamento pulpar para preservar o dente vivo.",
     "itens": ["Restauração em resina composta", "Capeamento pulpar", "Troca de restaurações antigas", "Tratamento de sensibilidade"]},
    {"id": "cirurgia", "nome": "Cirurgias e siso", "icon": "plus", "img": "img/fotos/siso-caso.jpg",
     "curto": "Extrações e cirurgias com planejamento radiográfico e suporte.",
     "texto": "Cirurgia exige planejamento, estrutura e acompanhamento depois do procedimento. Tudo é feito com avaliação radiográfica e suporte ao paciente do início ao fim.",
     "itens": ["Extração de siso", "Extrações simples", "Avaliação radiográfica", "Acompanhamento pós-operatório"]},
    {"id": "harmonizacao", "nome": "Harmonização facial", "icon": "face", "img": "img/fotos/melina-sorriso.jpg",
     "curto": "Procedimentos faciais com a Dra. Bárbara Herculano.",
     "texto": "A equipe conta com a Dra. Bárbara Herculano para harmonização facial, sempre com avaliação prévia e resultados que respeitam os traços de cada paciente.",
     "itens": ["Avaliação facial", "Preenchimentos", "Planejamento individual", "Retorno de acompanhamento"]},
]

EQUIPE = [
    ("melina", "Dra. Melina Corradi", "Responsável técnica e protesista", "CRO-MG 47295", "Cirurgiã-dentista apaixonada por transformar sorrisos com atendimento humanizado."),
    ("franklin", "Dr. Franklin Araújo", "Ortodontista e ortopedista facial", "CRO 52709", "Alinhamento dentário, harmonia facial e saúde do sorriso."),
    ("lucas", "Dr. Lucas Dias", "Implantodontista e cirurgião", "CRO 44622", "Excelência e dedicação para devolver função e qualidade de vida."),
    ("laysa", "Laysa Araújo", "Secretária", "Recepção", "Quem recebe cada paciente com carinho, atenção e dedicação."),
]

PASSOS = [
    ("Avaliação", "Você conta o que incomoda e o que deseja. A doutora examina com calma e, se preciso, pede radiografias."),
    ("Diagnóstico claro", "Tudo explicado com transparência: o que é necessário agora, o que pode esperar e as opções de tratamento."),
    ("Plano sob medida", "Etapas, prazos e valores definidos antes de começar, para você decidir sem pressa."),
    ("Tratamento e retorno", "Cuidado em cada etapa e retornos programados para manter o resultado por muito tempo."),
]

FAQ = [
    ("Preciso de avaliação antes do clareamento?", "Sim. O clareamento só é indicado depois da avaliação e da limpeza, para conferir a saúde dos dentes e da gengiva e escolher o protocolo certo para você."),
    ("Quanto tempo leva um implante?", "Depende da condição óssea e da cicatrização de cada paciente. Em muitos casos a reabilitação fica pronta em cerca de 90 dias, sempre com planejamento individual."),
    ("Qual aparelho é melhor para mim?", "Convencional, estético, autoligado ou alinhadores: cada um tem indicação própria. Na avaliação com o ortodontista você conhece as opções para o seu caso."),
    ("De quanto em quanto tempo devo fazer limpeza?", "A maioria dos pacientes se beneficia de uma limpeza profissional a cada seis meses, mas a frequência ideal é definida na consulta."),
    ("Quais os dias de atendimento?", "A clínica atende de segunda a sábado, com hora marcada. Agende pelo formulário ou chame no WhatsApp."),
]

FORM_TRAT = ["Avaliação", "Clareamento", "Implante", "Prótese ou coroa", "Aparelho ortodôntico", "Limpeza",
             "Restauração", "Siso ou extração", "Harmonização facial", "Dor ou urgência"]

# mosaico de resultados e posts: (arquivo, legenda, largo?)
POSTS = [
    ("coroa", "Coroa total: antes e depois", True),
    ("implante-caso", "Implante dentário: radiografia antes, durante e depois", False),
    ("limpeza-caso", "Após três sessões de limpeza", False),
    ("restauracao-2", "Capeamento pulpar e restauração em resina", False),
    ("siso-caso", "Caso clínico: remoção de siso com acompanhamento radiográfico", False),
    ("protese", "Prótese total caracterizada", False),
    ("ortodontia", "Tipos de aparelho ortodôntico", False),
    ("limpeza-post", "A importância da limpeza dental", False),
    ("clarea-day", "Semana do Clarea Day", False),
    ("black-premium", "Clareamento combinado", False),
    ("sorriso", "Sorriso planejado", False),
]

_S = 'viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"'
TOOTH = "M7.2 3.5c-2.6 0-4.2 2.2-4.2 5 0 2.3 1.1 3.6 1.6 5.6.6 2.4.7 6.4 2.7 6.4 1.7 0 1.6-4.3 3-5.6.4-.4 1-.4 1.4 0 1.4 1.3 1.3 5.6 3 5.6 2 0 2.1-4 2.7-6.4.5-2 1.6-3.3 1.6-5.6 0-2.8-1.6-5-4.2-5-1.9 0-2.6 1-3.6 1s-2.1-1-4-1z"
ICONS = {
    "arrow": f'<svg class="arrow" {_S}><path d="M5 12h14M13 6l6 6-6 6"/></svg>',
    "up": f'<svg {_S}><path d="M12 19V5M6 11l6-6 6 6"/></svg>',
    "close": f'<svg {_S}><path d="M6 6l12 12M18 6 6 18"/></svg>',
    "check": f'<svg {_S}><path d="M5 12.5l4.2 4L19 7"/></svg>',
    "play": '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M8 5v14l11-7z"/></svg>',
    "pin": f'<svg {_S}><path d="M12 21s-7-6.2-7-11.5A7 7 0 0 1 19 9.5C19 14.8 12 21 12 21z"/><circle cx="12" cy="9.5" r="2.5"/></svg>',
    "route": f'<svg {_S}><circle cx="6" cy="19" r="2"/><circle cx="18" cy="5" r="2"/><path d="M8 19h7a3.5 3.5 0 0 0 0-7H9a3.5 3.5 0 0 1 0-7h7"/></svg>',
    "calendar": f'<svg {_S}><rect x="3.5" y="5" width="17" height="15.5" rx="2"/><path d="M3.5 10h17M8 3v4M16 3v4"/></svg>',
    "clock": f'<svg {_S}><circle cx="12" cy="12" r="8.5"/><path d="M12 7.5V12l3 2"/></svg>',
    "sparkle": f'<svg {_S}><path d="M12 3c.6 4.2 2.8 6.4 7 7-4.2.6-6.4 2.8-7 7-.6-4.2-2.8-6.4-7-7 4.2-.6 6.4-2.8 7-7z"/><path d="M19 16c.2 1.4.9 2.1 2.3 2.3-1.4.2-2.1.9-2.3 2.3-.2-1.4-.9-2.1-2.3-2.3 1.4-.2 2.1-.9 2.3-2.3z"/></svg>',
    "tooth": f'<svg {_S}><path d="{TOOTH}"/></svg>',
    "implant": f'<svg {_S}><path d="M7 4.5c0-1 1-1.5 2.2-1.5h5.6C16 3 17 3.5 17 4.5c0 2-1.5 3.5-5 3.5S7 6.5 7 4.5z"/><path d="M9 10h6M9.5 13h5M10 16h4M10.5 19h3M12 8v13"/></svg>',
    "braces": f'<svg {_S}><path d="M3 9c3 2.2 6 3 9 3s6-.8 9-3"/><path d="M3 15c3-2.2 6-3 9-3s6 .8 9 3"/><rect x="5.5" y="9.6" width="2.6" height="2.6" rx=".5"/><rect x="10.7" y="10.6" width="2.6" height="2.6" rx=".5"/><rect x="15.9" y="9.6" width="2.6" height="2.6" rx=".5"/></svg>',
    "shield": f'<svg {_S}><path d="M12 3l7 3v5.5c0 4.4-3 8-7 9.5-4-1.5-7-5.1-7-9.5V6z"/><path d="M9 12l2 2 4-4"/></svg>',
    "drop": f'<svg {_S}><path d="M12 3.5s6 6.4 6 10.5a6 6 0 0 1-12 0c0-4.1 6-10.5 6-10.5z"/><path d="M9.5 14.5a2.6 2.6 0 0 0 2.5 2.4"/></svg>',
    "plus": f'<svg {_S}><rect x="3.5" y="3.5" width="17" height="17" rx="5"/><path d="M12 8v8M8 12h8"/></svg>',
    "face": f'<svg {_S}><path d="M12 3c-4 0-6.5 3-6.5 7.5 0 5 3.2 10.5 6.5 10.5s6.5-5.5 6.5-10.5C18.5 6 16 3 12 3z"/><path d="M9.5 15c1.4 1 3.6 1 5 0M9.3 10.2h.01M14.7 10.2h.01"/></svg>',
    "heart": f'<svg {_S}><path d="M12 20s-7.5-4.6-7.5-10.2A4.3 4.3 0 0 1 12 7.4a4.3 4.3 0 0 1 7.5 2.4C19.5 15.4 12 20 12 20z"/></svg>',
    "award": f'<svg {_S}><circle cx="12" cy="9" r="5.5"/><path d="M8.5 13.3 7 21l5-2.6 5 2.6-1.5-7.7"/></svg>',
    "instagram": f'<svg {_S}><rect x="3.5" y="3.5" width="17" height="17" rx="5"/><circle cx="12" cy="12" r="3.8"/><circle cx="17.2" cy="6.8" r=".6" fill="currentColor"/></svg>',
    "whatsapp": '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M17.47 14.38c-.3-.15-1.75-.86-2.02-.96-.27-.1-.47-.15-.67.15-.2.3-.77.96-.94 1.16-.17.2-.35.22-.64.07-.3-.15-1.25-.46-2.38-1.47-.88-.79-1.47-1.76-1.65-2.05-.17-.3-.02-.46.13-.6.13-.14.3-.35.45-.52.15-.17.2-.3.3-.5.1-.2.05-.37-.02-.52-.08-.15-.67-1.6-.92-2.2-.24-.58-.49-.5-.67-.5h-.57c-.2 0-.52.07-.8.37-.27.3-1.04 1.02-1.04 2.48s1.07 2.88 1.21 3.07c.15.2 2.1 3.2 5.08 4.49.71.3 1.27.49 1.7.63.72.23 1.37.2 1.88.12.57-.09 1.75-.72 2-1.41.25-.7.25-1.29.17-1.41-.07-.13-.27-.2-.57-.35zM12.05 21.5h-.01a9.45 9.45 0 0 1-4.82-1.32l-.35-.2-3.58.94.96-3.49-.23-.36a9.43 9.43 0 0 1-1.45-5.03c0-5.22 4.25-9.47 9.48-9.47 2.53 0 4.9.99 6.7 2.78a9.4 9.4 0 0 1 2.77 6.7c0 5.23-4.25 9.45-9.47 9.45zm8.06-17.52A11.33 11.33 0 0 0 12.05.64C5.77.64.66 5.75.66 12.03c0 2 .52 3.96 1.52 5.69L.57 23.6l6.03-1.58a11.36 11.36 0 0 0 5.44 1.39h.01c6.28 0 11.39-5.11 11.39-11.39 0-3.04-1.18-5.9-3.33-8.05z"/></svg>',
}
ARROW = ICONS["arrow"]


def wa(msg=WA_MSG):
    return f"https://wa.me/{PERFIL['wa']}?text={quote(msg)}"


def map_embed():
    return f"https://www.google.com/maps?q={quote_plus(PERFIL['q'])}&output=embed"


def route_link():
    return f"https://www.google.com/maps/dir/?api=1&destination={quote_plus(PERFIL['q'])}"


def a(s):
    return escape(s, quote=True)


def reel(rid, extra=""):
    _, cat, titulo, cap = REEL[rid]
    return (f'<button type="button" class="reel{extra}" data-full="assets/video/full/{rid}.mp4" data-title="{a(titulo)}" '
            f'data-cap="{a(cap)}" data-cat="{a(cat)}" data-ig="https://www.instagram.com/reel/{rid}/" aria-label="Assistir: {a(titulo)}">'
            f'<img src="assets/img/reels/{rid}.jpg" alt="{a(titulo)}: {a(cap)}" loading="lazy" width="720" height="1280">'
            f'<video muted loop playsinline preload="none" data-src="assets/video/p/{rid}.mp4"></video>'
            f'<span class="reel-play">{ICONS["play"]}</span>'
            f'<span class="reel-info"><span class="label">{cat}</span><strong>{titulo}</strong></span></button>')


def rail(ids=None):
    return f'<div class="reel-rail" data-rail>{"".join(reel(i) for i in (ids or DESTAQUE))}</div>'


def trat_grid():
    cards = []
    for i, t in enumerate(TRATAMENTOS):
        cards.append(f'<a class="tcard" href="tratamentos.html#{t["id"]}" data-reveal style="--rd:{(i % 4) * .07:.2f}s">'
                     f'<span class="tcard-ic">{ICONS[t["icon"]]}</span><span class="n">{i + 1:02d}</span>'
                     f'<h3>{t["nome"]}</h3><p>{t["curto"]}</p><span class="go">Saiba mais {ARROW}</span></a>')
    return f'<div class="tgrid">{"".join(cards)}</div>'


def trat_full():
    out = []
    for i, t in enumerate(TRATAMENTOS):
        itens = "".join(f"<li>{ICONS['check']}{x}</li>" for x in t["itens"])
        out.append(f'<article class="tfull{" rev" if i % 2 else ""}" id="{t["id"]}">'
                   f'<div class="tfull-media" data-mask><img src="assets/{t["img"]}" alt="{a(t["nome"])}" loading="lazy"></div>'
                   f'<div class="tfull-body" data-reveal><span class="label">{i + 1:02d} · Tratamento</span>'
                   f'<h2 class="display md">{t["nome"]}</h2><p class="lead">{t["texto"]}</p><ul class="checks">{itens}</ul>'
                   f'<div class="btn-row"><a class="btn" href="agendamento.html?tratamento={quote(t["nome"])}">Agendar avaliação {ARROW}</a></div></div></article>')
    return "".join(out)


def equipe():
    cards = []
    for i, (img, nome, cargo, cro, txt) in enumerate(EQUIPE):
        cards.append(f'<article class="member" data-reveal style="--rd:{i * .08:.2f}s">'
                     f'<div class="member-photo"><img src="assets/img/fotos/{img}.jpg" alt="{a(nome)}, {a(cargo)}" loading="lazy"></div>'
                     f'<div class="member-body"><span class="label">{cro}</span><h3>{nome}</h3><p class="role">{cargo}</p><p>{txt}</p></div></article>')
    return f'<div class="team">{"".join(cards)}</div>'


def passos():
    return '<ol class="steps">' + "".join(
        f'<li class="step" data-reveal style="--rd:{i * .1:.2f}s"><b>{i + 1:02d}</b><h3>{t}</h3><p>{d}</p></li>'
        for i, (t, d) in enumerate(PASSOS)) + "</ol>"


def faq():
    return '<div class="faq">' + "".join(
        f'<details data-reveal><summary><span>{q}</span><i aria-hidden="true"></i></summary><p>{r}</p></details>' for q, r in FAQ) + "</div>"


def compare():
    return (f'<div class="compare" data-compare style="--pos:50%">'
            f'<img src="assets/img/fotos/coroa-depois.jpg" alt="Depois: dente restaurado com coroa total" loading="lazy">'
            f'<div class="compare-before"><img src="assets/img/fotos/coroa-antes.jpg" alt="Antes: dente comprometido" loading="lazy"></div>'
            f'<span class="compare-tag l">Antes</span><span class="compare-tag r">Depois</span>'
            f'<input type="range" min="0" max="100" value="50" aria-label="Arraste para comparar antes e depois">'
            f'<span class="compare-handle" aria-hidden="true"><i>{ARROW}</i></span></div>')


def posts():
    tiles = "".join(f'<button type="button" class="post{" wide" if w else ""}" data-img="assets/img/fotos/{f}.jpg" data-title="{a(c)}" data-reveal>'
                    f'<img src="assets/img/fotos/{f}.jpg" alt="{a(c)}" loading="lazy"><span class="cap">{c}</span></button>' for f, c, w in POSTS)
    return f'<div class="posts">{tiles}</div>'


def form():
    chips = "".join(f'<label class="chip"><input type="checkbox" name="tratamento" value="{s}"><span>{s}</span></label>' for s in FORM_TRAT)
    per = "".join(f'<label class="chip"><input type="radio" name="periodo" value="{p}"><span>{p}</span></label>' for p in ("Manhã", "Tarde", "Tanto faz"))
    pac = "".join(f'<label class="chip"><input type="radio" name="paciente" value="{p}"><span>{p}</span></label>' for p in ("Primeira consulta", "Já sou paciente"))
    return f"""<form class="form" data-wa-form data-wa="{PERFIL['wa']}" novalidate>
  <div class="row">
    <label data-field="nome"><span>Seu nome <b>*</b></span><input name="nome" autocomplete="name" placeholder="Como podemos te chamar?" required><em class="err">Diga o seu nome.</em></label>
    <label data-field="idade"><span>Idade <b>*</b></span><input name="idade" type="number" inputmode="numeric" min="1" max="120" placeholder="Ex.: 32" required><em class="err">Informe a idade.</em></label>
  </div>
  <fieldset data-field="tratamento">
    <legend>Tratamento desejado <b>*</b></legend>
    <div class="chips">{chips}</div>
    <em class="err">Escolha pelo menos uma opção.</em>
  </fieldset>
  <div class="row">
    <label data-field="data"><span>Data sugerida <b>*</b></span><input name="data" type="date" required><em class="err">Escolha uma data.</em></label>
    <label><span>Horário sugerido</span><input name="hora" type="time" step="900"></label>
  </div>
  <div class="row">
    <fieldset><legend>Período</legend><div class="chips">{per}</div></fieldset>
    <fieldset><legend>Você é</legend><div class="chips">{pac}</div></fieldset>
  </div>
  <label><span>Quer contar algo?</span><textarea name="obs" placeholder="Ex.: sinto sensibilidade, quero clarear para um casamento, perdi um dente..."></textarea></label>
  <div class="form-foot">
    <small>Ao enviar, o WhatsApp abre com tudo preenchido. O horário é confirmado pela recepção.</small>
    <button class="btn btn-wa" type="submit">{ICONS['whatsapp']} Enviar pelo WhatsApp</button>
  </div>
</form>"""


def cur(key, current):
    return ' aria-current="page"' if key == current else ""


def brand():
    return '<span class="brand-name">Melina Corradi<small>Odontologia</small></span>'


def header(current):
    links = "".join(f'<a class="nav-link" href="{h}"{cur(k, current)}>{l}</a>' for k, l, h, top in NAV if top and k not in ("agendamento", "contato"))
    over = "".join(f'<li><a href="{h}"{cur(k, current)}><span>{i:02d}</span>{l}</a></li>' for i, (k, l, h, _) in enumerate(NAV, 1))
    return f"""<a class="skip" href="#conteudo">Pular para o conteúdo</a>
<div class="progress-bar" aria-hidden="true"></div>
<header class="site-header">
  <div class="wrap">
    <a class="brand" href="index.html" aria-label="Dra. Melina Corradi, página inicial">{brand()}</a>
    <nav class="nav" aria-label="Principal">
      {links}
      <a class="nav-link" href="contato.html"{cur('contato', current)}>Contato</a>
      <a class="btn btn-sm" href="agendamento.html"{cur('agendamento', current)}>Agendar {ARROW}</a>
      <button class="menu-toggle" type="button" aria-expanded="false" aria-controls="menu" aria-label="Abrir menu"><span class="bars"></span></button>
    </nav>
  </div>
</header>
<div class="overlay" id="menu" data-open="false" aria-hidden="true" inert>
  <ol>{over}</ol>
  <div class="overlay-foot">
    <a class="btn" href="agendamento.html">Agendar avaliação {ARROW}</a>
    <a href="{wa()}" target="_blank" rel="noopener">{ICONS['whatsapp']} {PERFIL['wa_fone']}</a>
    <a href="{PERFIL['instagram']}" target="_blank" rel="noopener">{ICONS['instagram']} @dra.mellcorr</a>
  </div>
</div>
"""


def footer():
    navs = "".join(f'<li><a href="{h}">{l}</a></li>' for _, l, h, _t in NAV)
    trs = "".join(f'<li><a href="tratamentos.html#{t["id"]}">{t["nome"]}</a></li>' for t in TRATAMENTOS[:6])
    return f"""<footer class="site-footer">
  <div class="wrap">
    <div class="foot-cta">
      <div>
        <span class="label">Agenda aberta</span>
        <p class="foot-lead">Seu sorriso merece <em>cuidado de verdade.</em></p>
      </div>
      <div class="btn-row">
        <a class="btn btn-light" href="agendamento.html">Agendar avaliação {ARROW}</a>
        <a class="btn btn-line" href="{wa()}" target="_blank" rel="noopener">{ICONS['whatsapp']} WhatsApp</a>
      </div>
    </div>
    <div class="foot-grid">
      <div class="intro">
        <a class="brand" href="index.html" aria-label="Dra. Melina Corradi">{brand()}</a>
        <p>Transformando sorrisos com naturalidade em Mateus Leme. {PERFIL['cro']}.</p>
        <div class="foot-social">
          <a href="{PERFIL['instagram']}" target="_blank" rel="noopener" aria-label="Instagram">{ICONS['instagram']}</a>
          <a href="{wa()}" target="_blank" rel="noopener" aria-label="WhatsApp">{ICONS['whatsapp']}</a>
          <a href="{route_link()}" target="_blank" rel="noopener" aria-label="Como chegar">{ICONS['route']}</a>
        </div>
      </div>
      <div><h4>Navegação</h4><ul>{navs}</ul></div>
      <div><h4>Tratamentos</h4><ul>{trs}</ul></div>
      <div><h4>Consultório</h4><ul>
        <li>{PERFIL['rua']}<br>{PERFIL['bairro']} · {PERFIL['cidade']}</li>
        <li>{PERFIL['horario']}</li>
        <li><a href="{wa()}" target="_blank" rel="noopener">{PERFIL['wa_fone']}</a></li>
        <li><a href="{route_link()}" target="_blank" rel="noopener">Como chegar</a></li>
      </ul></div>
    </div>
    <div class="foot-bottom">
      <span>&copy; <span data-year>2026</span> Dra. Melina Corradi · {PERFIL['cro']} · Responsável técnica</span>
      <a class="dev-by" href="https://achillesmedia.com.br" target="_blank" rel="noopener">Desenvolvido por <strong>Achilles</strong></a>
      <button class="to-top" type="button" data-top>Voltar ao topo {ICONS['up']}</button>
    </div>
  </div>
</footer>
<a class="wa-float" href="{wa()}" target="_blank" rel="noopener" aria-label="Conversar no WhatsApp">{ICONS['whatsapp']}<span>Agende pelo WhatsApp</span></a>
<div class="vmodal" id="vmodal" aria-hidden="true" role="dialog" aria-modal="true" aria-label="Vídeo" inert>
  <div class="vmodal-box">
    <video controls playsinline preload="none"></video>
    <div class="vmodal-side"><span class="label vm-cat"></span><h3 class="vm-title"></h3><p class="vm-cap"></p>
      <div class="btn-row"><a class="btn btn-sm" href="agendamento.html">Agendar avaliação {ARROW}</a><a class="btn btn-line btn-sm vm-ig" href="{PERFIL['instagram']}" target="_blank" rel="noopener">{ICONS['instagram']} Ver no Instagram</a></div>
    </div>
  </div>
  <button class="vmodal-close" type="button" aria-label="Fechar vídeo">{ICONS['close']}</button>
</div>
<dialog class="lightbox" aria-label="Imagem ampliada"><img src="" alt=""><p class="label"></p><button type="button" class="lb-close" aria-label="Fechar">{ICONS['close']}</button></dialog>
"""


def page_url(name):
    return f"{SITE}/" if name == "index" else f"{SITE}/{name}.html"


def page(meta, body, name):
    title = meta["title"]
    full = f"{title} | Dra. Melina Corradi" if name != "index" else title
    url = page_url(name)
    ld = {"@context": "https://schema.org", "@type": "Dentist", "name": "Dra. Melina Corradi Odontologia", "url": SITE,
          "image": f"{SITE}/assets/og-melina.jpg", "telephone": "+55 31 99780-1670",
          "address": {"@type": "PostalAddress", "streetAddress": PERFIL["rua"], "addressLocality": "Mateus Leme",
                      "addressRegion": "MG", "addressCountry": "BR"},
          "openingHours": "Mo-Sa", "sameAs": [PERFIL["instagram"]]}
    return f"""<!doctype html>
<html lang="pt-BR" class="no-js">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{full}</title>
<meta name="description" content="{meta['description']}">
<meta name="theme-color" content="#f6f4ee">
<link rel="canonical" href="{url}">
<meta property="og:type" content="website">
<meta property="og:locale" content="pt_BR">
<meta property="og:title" content="{full}">
<meta property="og:description" content="{meta['description']}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{SITE}/assets/og-melina.jpg">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="assets/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="assets/apple-touch-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,500;0,600;1,400;1,500&family=Geist:wght@300..600&family=Geist+Mono:wght@400..500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="assets/css/style.css?v={V}">
<script>document.documentElement.classList.replace('no-js','js')</script>
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
</head>
<body data-page="{name}">
{header(meta.get('nav', name))}
<main id="conteudo">
{body.strip()}
</main>
{footer()}<script src="assets/js/main.js?v={V}" defer></script>
</body>
</html>
"""


def render(body):
    rep = {
        "{{ARROW}}": lambda: ARROW, "{{WA}}": wa, "{{WA_FONE}}": lambda: PERFIL["wa_fone"], "{{IG}}": lambda: PERFIL["instagram"],
        "{{ENDERECO}}": lambda: f"{PERFIL['rua']}, {PERFIL['bairro']}, {PERFIL['cidade']}", "{{HORARIO}}": lambda: PERFIL["horario"],
        "{{CRO}}": lambda: PERFIL["cro"], "{{ROTA}}": route_link, "{{MAPA}}": map_embed, "{{RAIL}}": rail,
        "{{RAIL_ALL}}": lambda: rail([r[0] for r in REELS]), "{{TRAT_GRID}}": trat_grid, "{{TRAT_FULL}}": trat_full,
        "{{EQUIPE}}": equipe, "{{PASSOS}}": passos, "{{FAQ}}": faq, "{{COMPARE}}": compare, "{{POSTS}}": posts, "{{FORM}}": form,
    }
    for k, f in rep.items():
        if k in body:
            body = body.replace(k, f())
    body = re.sub(r"\{\{REEL:([\w-]+)\}\}", lambda m: reel(m.group(1), " solo"), body)
    return re.sub(r"\{\{ICON:(\w+)\}\}", lambda m: ICONS[m.group(1)], body)


def main():
    urls = []
    for src in sorted(PAGES.glob("*.html")):
        raw = src.read_text(encoding="utf-8")
        m = re.match(r"\s*<!--meta\s*(\{.*?\})\s*-->", raw, re.S)
        if not m:
            raise SystemExit(f"{src.name}: faltando bloco <!--meta-->")
        meta = json.loads(m.group(1))
        html = page(meta, render(raw[m.end():]), src.stem)
        for bad in ("—", "–"):
            if bad in html:
                raise SystemExit(f"{src.name}: contém travessão ({bad!r}); troque por outra pontuação")
        if "{{" in html:
            raise SystemExit(f"{src.name}: marcador não substituído")
        (OUT / f"{src.stem}.html").write_text(html, encoding="utf-8")
        urls.append(page_url(src.stem))
        print("ok", src.stem + ".html")
    (OUT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
        + "".join(f"<url><loc>{u}</loc></url>" for u in urls) + "</urlset>\n", encoding="utf-8")


if __name__ == "__main__":
    main()
