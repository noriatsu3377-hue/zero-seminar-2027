#!/usr/bin/env python3
"""data/seminars.json からトップページと各セミナー詳細ページを生成する。

使い方:  python3 build.py
日程・受講条件などは data/seminars.json だけを編集すれば、全ページに反映される。
詳細ページは seminars/<slug>/index.html に出力するので、GitHub Pages で
/seminars/<slug>/ に直接アクセス・再読み込みしても 404 にならない。
"""
import json
import html
import os
import hashlib

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA = json.load(open(os.path.join(ROOT, 'data', 'seminars.json'), encoding='utf-8'))
SITE, INS, SEMS = DATA['site'], DATA['instructor'], DATA['seminars']
BY = {s['slug']: s for s in SEMS}
RELEASE_OF = {slug: r for r in SITE['release'] for slug in r['slugs']}
E = html.escape
ASSET_VERSIONS = {name: hashlib.sha256(open(os.path.join(ROOT, "assets", name), "rb").read()).hexdigest()[:12] for name in ("style.css", "main.js")}


STATUS_LABEL = {'before': '受付前', 'open': '受付中', 'full': '満席', 'closed': '受付終了', 'finished': '開催終了'}
OUTLINE_ROWS = [('time', '時間'), ('venue', '会場・アクセス'), ('price', '受講料'), ('capacity', '定員'), ('items', '持ち物・服装'),
                ('deadline', '申込期限'), ('payment', '支払い方法'), ('cancel', 'キャンセル条件')]
PENDING_TXT = '受付開始時にご案内します'


def status(s):
    st = s.get('status', 'before')
    if st == 'before':
        return f"受付前（{RELEASE_OF[s['slug']]['month']}受付開始予定）"
    return STATUS_LABEL[st]


def can_apply(s):
    # 受付中かつ正式な申込URLがある場合のみ「申し込む」を出す。受付開始月から自動で受付中にはしない。
    return s.get('status') == 'open' and bool(s.get('apply_url'))


def line_button(base, label='公式LINEで受付案内を受け取る', cls='btn solid'):
    if SITE['line_url']:
        return f'<a class="{cls}" href="{E(SITE["line_url"])}" rel="noopener">{label}</a>'
    return f'<span class="btn disabled" aria-disabled="true">{label}<small style="font-size:.75em">（準備中）</small></span>'


def cta(s, base, cls='btn solid'):
    if can_apply(s):
        return f'<a class="{cls}" href="{E(s["apply_url"])}" rel="noopener">{E(s["name"])}に申し込む</a>'
    st = s.get('status', 'before')
    label = {'full': '公式LINEで次回の案内を受け取る', 'closed': '公式LINEで次回の案内を受け取る',
             'finished': '公式LINEで次回の案内を受け取る'}.get(st, '公式LINEで受付案内を受け取る')
    return line_button(base, label, cls)


def ov(s, key):
    v = (s.get('outline') or {}).get(key, '')
    return E(v) if v else PENDING_TXT


def head(title, desc, base):
    return f'''<!DOCTYPE html>
<html lang="ja" class="no-js">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
<title>{E(title)}</title>
<meta name="description" content="{E(desc)}">
<meta property="og:title" content="{E(title)}">
<meta property="og:description" content="{E(desc)}">
<meta property="og:type" content="website">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Cinzel:wght@400;500&family=Noto+Sans+JP:wght@400;500&family=Noto+Serif+JP:wght@500&display=swap">
<link rel="stylesheet" href="{base}assets/style.css?v={ASSET_VERSIONS["style.css"]}">
<script src="{base}assets/main.js?v={ASSET_VERSIONS["main.js"]}" defer></script>
</head>
<body class="has-sticky">
<a class="skip" href="#main">本文へ移動</a>
<header class="site-header"><div class="wrap">
  <a class="brand" href="{base}">ZERO<small>零式 2027 年間セミナー</small></a>
  <nav class="nav" aria-label="サイト内">
    <a href="{base}#schedule">年間スケジュール</a><a href="{base}#instructor">講師</a><a href="{base}#seminars">セミナー一覧</a><a href="{base}#entry">受付・申込</a>
  </nav>
  <details class="mobile-menu"><summary>メニュー</summary><nav aria-label="スマートフォンのサイト内メニュー"><a href="{base}#schedule">年間スケジュール</a><a href="{base}#instructor">講師プロフィール</a><a href="{base}#seminars">セミナー一覧</a><a href="{base}#entry">受付・申込</a></nav></details>
</div></header>
'''


def foot(base, sticky):
    return f'''<footer class="site-footer">
  <p><a href="{base}">トップページ</a> ／ <a href="{base}#schedule">年間スケジュール</a></p>
  <p>© 2027 ZERO METHODOLOGY / TOTAL BODY FITNESS THEORY</p>
</footer>
<div class="sticky-cta">{sticky}</div>
</body>
</html>
'''


def card(s, base):
    url = f'{base}seminars/{s["slug"]}/'
    topics = '|'.join(s.get('topics') or [])
    tags = ''.join(f'<span class="tag-topic">{E(t)}</span>' for t in s.get('topics') or [])
    return f'''<article class="card fade" data-month="{s['month']}" data-topics="{E(topics)}">
  <img src="{base}{s['image']}" alt="{E(s['image_alt'])}（過去のセミナーの様子）" loading="lazy" width="800" height="500">
  <div class="card-body">
    <div class="lv">{s['month']}月｜{E(s['level'])}</div>
    <h3>{E(s['name'])}</h3>
    <a class="btn" href="{url}" aria-label="{E(s['name'])}のセミナー詳細を見る">セミナー詳細を見る</a>
    <p>{E(s['summary'])}</p>
    <dl>
      <dt>日程</dt><dd>{E(s['date'])}（{E(s['place'])}）</dd>
      <dt>形式</dt><dd>{E(s['format'])}</dd>
      <dt>受講条件</dt><dd>{E(s['condition'])}</dd>
      <dt>受付</dt><dd>{E(status(s))}</dd>
    </dl>
    <div class="tags">{tags}</div>
  </div>
</article>'''


def build_index():
    base = ''
    rows = ''
    for s in SEMS:
        place_cls = 'chip place-kochi' if s['place'] != '東京' else 'chip'
        rows += f'''<div class="row">
  <div class="m">{s['month']:02d}</div>
  <div class="d">{E(s['date'])}</div>
  <div class="t"><a href="seminars/{s['slug']}/" aria-label="{E(s['name'])}の詳細ページ">{E(s['name'])}</a><small>{E(s['format'])}｜受講条件：{E(s['condition'])}</small></div>
  <div class="s"><span class="{place_cls}">{E(s['place'])}</span> <span class="chip status">{E(RELEASE_OF[s['slug']]['month'])}受付開始</span></div>
</div>
'''
    cards = '\n'.join(card(s, base) for s in SEMS)
    month_opts = ''.join(f'<option value="{s["month"]}">{s["month"]}月：{E(s["name"])}</option>' for s in SEMS)
    topic_btns = ''.join(f'<button type="button" class="topic" aria-pressed="false" data-topic="{E(t)}">{E(t)}</button>' for t in SITE['topics'])
    rel = ''
    for r in SITE['release']:
        items = ''.join(f'<li><a href="seminars/{x}/">{E(BY[x]["name"])}</a></li>' for x in r['slugs'])
        rel += f'<div class="rel"><div class="when">{E(r["month"])}</div><div>{E(r["label"])}</div><ul>{items}</ul></div>'
    certs = ''.join(f'<li>{E(c)}</li>' for c in INS['certs_private'])
    trains = ''.join(f'<li>{E(c)}</li>' for c in INS['trainings'])
    acts = ''.join(f'<li>{E(c)}</li>' for c in INS['activities'])
    out = head('零式 2027 年間セミナー｜東京から、零式を学ぶ一年。',
               'トレーナー・セラピストのための零式セミナー。2027年は東京を中心に、手・足の入門講座から零式-ヘッドコンディショニング極、関節調整法、ZERO RECOVERYまで、毎月1講座を開催します。', base)
    out += f'''<main id="main">
<section class="hero">
  <div class="hero-photo" style="background-image:url('images/hero-assessment.jpg')" role="img" aria-label="受講者の肩まわりを評価する講師・原口慶篤"></div>
  <div class="hero-grad" aria-hidden="true"></div>
  <div class="wrap">
    <p class="hero-year">ZERO SEMINAR 2027</p>
    <h1>東京から、<br>零式を学ぶ一年。</h1>
    <p class="hero-sub">トレーナー・セラピストなど、身体に関わる専門職の方へ。<br>「触れる手」をつくる入門講座から、零式の技術を統合する上位講座まで。2027年は東京を中心に、毎月1講座を開催します。</p>
    <ul class="hero-facts">
      <li>全12講座・各講座は年1回の開催</li>
      <li>東京開催（7月のみ高知で合宿）</li>
      <li>土日中心（7月の合宿は月・祝を含む）</li>
    </ul>
    <div class="btns">
      <a class="btn solid" href="#schedule">年間スケジュールを見る</a>
      {line_button(base, "公式LINEで受付案内を受け取る", "btn")}
    </div>
  </div>
  <button class="motion-toggle" type="button" aria-pressed="false">背景の動きを停止</button>
</section>

<section class="sec-ivory">
  <div class="wrap intro fade">
    <img src="images/lecture-talk.jpg" alt="{E(INS['photo_alt'])}" width="440" height="587" loading="lazy">
    <div>
      <p class="eyebrow">INSTRUCTOR</p>
      <p class="name">{E(INS['name'])}<span style="font-size:.85rem;margin-left:10px;color:var(--ink-sub)">{E(INS['kana'])}</span></p>
      <p class="role">{E(' ／ '.join(INS['titles']))}<br>{E(INS['job'])}</p>
      <p>全講座を担当する講師です。パーソナルトレーナー・整体師として12年、現場でお客様に向き合いながら、人体解剖実習やオステオパシーで学びを重ねてきました。その経験を、トレーナー・セラピストが<span class="mk">現場で使える技術</span>として伝えています。</p>
      <a href="#instructor">講師の詳しいプロフィールを見る</a>
    </div>
  </div>
</section>

<section>
  <div class="wrap">
    <p class="eyebrow">LEARNING PATH</p>
    <h2>零式で学べること</h2>
    <p class="lead">零式の講座は、入門から統合までの段階に分かれています。<span class="mk">興味や目的に合わせて</span>講座を選べます。すべてを順番に受講する必要はありません。必要な修了歴や参加日数は、各講座の受講条件をご確認ください。</p>
    <div class="steps">
      <div class="step fade"><div class="lv">STEP 1｜入門</div><h3>手・足をつくる</h3><p>零式-「手」を作るセミナー／零式-足を作るセミナー。受講条件なし。</p></div>
      <div class="step fade"><div class="lv">STEP 2｜基幹</div><h3>零式-ヘッドコンディショニング極</h3><p>零式の中心となる技術。受講条件なし。</p></div>
      <div class="step fade"><div class="lv">STEP 3｜応用・上位</div><h3>姿勢・経絡・関節・内臓</h3><p>美姿勢、経絡ストレッチ、関節調整法、内臓調整など。関節調整法ADVANCEはBASIC修了者が対象。</p></div>
      <div class="step fade"><div class="lv">STEP 4｜統合</div><h3>ZERO RECOVERY</h3><p>零式の技術を統合する最上位講座。零式-ヘッドコンディショニング極の修了者が対象。</p></div>
    </div>
    <p class="cond">事前の修了歴が必要な講座：零式-関節調整法 ADVANCE（BASIC修了者）／零式-ZERO RECOVERY 第2期（零式-ヘッドコンディショニング極の修了者）</p>
  </div>
</section>

<section id="schedule" class="sec-charcoal">
  <div class="wrap">
    <p class="eyebrow">2027 SCHEDULE</p>
    <h2>年間スケジュール</h2>
    <p class="lead">各講座は年1回、1ヶ月に1講座の開催です。会場は<span class="mk">東京</span>、7月の合宿のみ高知で開催します。会場の詳細は受付開始時にご案内します。</p>
    <div class="sched">
{rows}    </div>
    <p class="note">※日程は予定です。変更がある場合は公式LINEでお知らせします。</p>
  </div>
</section>

<section id="instructor" class="sec-ivory">
  <div class="wrap profile">
    <figure class="fade">
      <img src="images/lecture-skeleton.jpg" alt="骨格模型を使って骨盤と背骨を説明する原口慶篤" width="800" height="1000" loading="lazy">
      <figcaption>セミナーでの講義の様子</figcaption>
    </figure>
    <div>
      <p class="eyebrow">PROFILE</p>
      <h2>{E(INS['name'])}</h2>
      <p class="role" style="color:var(--ink-sub)">{E(' ／ '.join(INS['titles']))}<br>{E(INS['job'])}</p>
      <p>パーソナルトレーナー・整体師として12年、現場でお客様の身体に向き合ってきました。人体解剖実習には5回参加し、オステオパシーではスラスト（BASIC・ADVANCE）と内臓調整を学んでいます。教科書の知識を、実際の身体で確かめてきた経験が、零式の講座の土台です。</p>
      <p>零式で大切にしているのは、<span class="mk">目の前の一人をよく見て、必要なことを、必要な分だけ</span>行うこと。技術を選ぶ理由にも、手を止める判断にも責任を持つ姿勢を、技術と一緒に伝えています。</p>
      <div class="pf-block"><h3>主な活動・指導実績</h3><ul>{acts}</ul></div>
      <div class="pf-block"><h3>民間資格</h3><ul>{certs}</ul></div>
      <div class="pf-block"><h3>研修・講習の受講歴</h3><ul>{trains}</ul></div>
      <p class="pf-note">※整体師は国家資格ではありません。</p>
    </div>
  </div>
</section>

<section id="seminars">
  <div class="wrap">
    <p class="eyebrow">SEMINARS</p>
    <h2>セミナー一覧</h2>
    <div class="common-info">
      <p><strong>対象：</strong>トレーナー・セラピストなど、身体に関わる専門職の方（受講条件のある講座は各カードに記載）</p>
      <p><strong>料金・時間・会場・定員：</strong>各講座の受付開始時にご案内します。講座の内容とカリキュラムは「セミナー詳細を見る」からご確認ください。</p>
    </div>
    <form class="filter" aria-label="セミナーの絞り込み" hidden>
      <div class="filter-row">
        <label for="f-month">開催月</label>
        <select id="f-month"><option value="">すべての月</option>{month_opts}</select>
      </div>
      <fieldset class="filter-row"><legend>学びたい内容</legend><div class="topic-btns">{topic_btns}</div></fieldset>
      <div class="filter-foot"><p class="count" role="status" aria-live="polite">全{len(SEMS)}講座を表示中</p><button type="button" class="btn reset">すべて表示に戻す</button></div>
    </form>
    <div class="cards">
{cards}
    </div>
    <p class="empty" hidden>条件に合う講座はありません。「すべて表示に戻す」で全講座を表示できます。</p>
    <p class="note">※カードの写真は過去のセミナーの様子です。</p>
  </div>
</section>

<section id="entry" class="sec-ivory">
  <div class="wrap">
    <p class="eyebrow">ENTRY</p>
    <h2>受付開始時期と、お申し込みの流れ</h2>
    <p class="lead">2027年の講座は4つの期間に分けて受付を開始します（2026年11月・2027年1月・4月・7月）。受付開始のお知らせは公式LINEでお届けします。</p>
    <div class="release">{rel}</div>
    <ol class="flow">
      <li>公式LINEで受付開始の案内を受け取る</li>
      <li>各講座の申込フォームから送信</li>
      <li>案内メールに沿ってお支払い</li>
      <li>入金確認後、正式申込完了</li>
    </ol>
  </div>
</section>

<section class="line-cta">
  <div class="wrap narrow">
    <p class="eyebrow">OFFICIAL LINE</p>
    <h2>受付開始のお知らせは、公式LINEから。</h2>
    <p class="lead">{'現在、2027年の講座はすべて受付前です。' if all(x.get('status','before')=='before' for x in SEMS) else '受付中の講座は各詳細ページからお申し込みいただけます。'}受付開始のご案内を公式LINEでお届けします。</p>
    <div class="btns">{line_button(base)}</div>
  </div>
</section>
</main>
'''
    out += foot(base, f'<a class="btn" href="#schedule">年間日程</a>{line_button(base, "LINE受付案内")}')
    open(os.path.join(ROOT, 'index.html'), 'w', encoding='utf-8').write('\n'.join(line.rstrip() for line in out.split('\n')))


def related_note(cur, x):
    pairs = {('kansetsu-basic', 'kansetsu-advance'): '続けて受講（BASIC修了が条件）',
             ('kansetsu-advance', 'kansetsu-basic'): 'ADVANCEの受講条件となる講座',
             ('zero-recovery', 'kiwami'): 'ZERO RECOVERYの受講条件',
             ('kiwami', 'zero-recovery'): '極の修了者が進める統合講座'}
    return pairs.get((cur, x), '')


def build_detail(s):
    base = '../../'
    pending = s.get('pending')
    li = lambda xs: ''.join(f'<li>{E(x)}</li>' for x in xs)
    title = f'{s["name"]}｜零式 2027 年間セミナー'
    desc = f'{s["name"]}（{s["date"]}・{s["place"]}）。{s["summary"]}'
    out = head(title, desc, base)
    cta_main = cta(s, base)

    def wait(what):
        return f'<div class="pending-box"><strong>情報待ち：</strong>{what}は確認中です。確定次第このページでご案内します。</div>'

    st = s.get('status', 'before')
    out += f'''<main id="main">
<div class="wrap crumb"><a href="{base}">トップ</a> ／ <a href="{base}#seminars">セミナー一覧</a> ／ {E(s['name'])}</div>
<div class="wrap d-hero">
  <figure class="d-photo"><img src="{base}{s['image']}" alt="{E(s['image_alt'])}" width="800" height="600"><figcaption>過去のセミナーの様子</figcaption></figure>
  <div class="d-head">
    <p class="eyebrow">{s['month']}月開催｜{E(s['level'])}</p>
    <h1>{E(s['name'])}</h1>
    <p class="catch">{E(s['catch'])}</p>
    <p>{E(s['summary'])}</p>
    <dl class="facts">
      <dt>日程</dt><dd>{E(s['date'])}</dd>
      <dt>会場</dt><dd>{E(s['place'])}</dd>
      <dt>形式</dt><dd>{E(s['format'])}</dd>
      <dt>受講条件</dt><dd>{E(s['condition'])}</dd>
      <dt>受付状況</dt><dd><span class="st st-{st}">{E(status(s))}</span></dd>
    </dl>
    <div class="btns">{cta_main}<a class="btn" href="{base}#schedule">年間スケジュールに戻る</a></div>
  </div>
</div>
'''
    toc = [] if pending else [('for-you', '対象者'), ('goals', '学習目標'), ('content', '講義・実技'), ('curriculum', 'カリキュラム'), ('diff', '他講座との違い')]
    toc += [('instructor', '講師'), ('outline', '開催概要')] + ([('faq', 'よくある質問')] if s.get('faq') else [])
    out += '<nav class="detail-nav wrap" aria-label="この講座のページ内目次">' + ''.join(f'<a href="#{i}">{t}</a>' for i, t in toc) + '</nav>\n'

    if pending:
        out += '''<section class="sec-ivory d-sec"><div class="wrap narrow">
  <h2>講座内容は詳細準備中です</h2>
  <div class="pending-box">2027年11月13日（土）に東京で開催を予定しています。講座名・内容・対象・受講条件は決まり次第、公式LINEとこのページでお知らせします。</div>
</div></section>
'''
    else:
        cur = s.get('curriculum')
        if cur:
            if cur.get('days'):
                body = ''.join(f'<div class="day"><h3>{E(d["title"])}</h3><ol>{li(d["items"])}</ol></div>' for d in cur['days'])
            else:
                body = f'<ol class="flow-list">{li(cur["steps"])}</ol>'
            notes = ''
            if cur.get('reference'):
                notes += '<p class="ref-note">過去の講座内容をもとにした参考カリキュラムです。2027年の実施内容は確定後に更新します。時間配分は受付開始時にご案内します。</p>'
            for k in ('source_note', 'extra'):
                if cur.get(k):
                    notes += f'<p class="ref-note">{E(cur[k])}</p>'
            cur_html = notes + body
        else:
            cur_html = wait('カリキュラム（講義と実技の順序）')

        if s.get('lecture') or s.get('practice'):
            content_html = (f'<div class="two-col"><div><h3>講義で扱う内容</h3><ul class="dots">{li(s.get("lecture", []))}</ul></div>'
                            f'<div><h3>実技で扱う内容</h3><ul class="dots">{li(s.get("practice", []))}</ul></div></div>')
            if cur and cur.get('reference'):
                content_html += '<p class="ref-note">過去の講座資料にもとづく内容です。2027年の内容は確定後に更新します。</p>'
        else:
            content_html = wait('講義と実技の具体的な内容')
        goals_html = f'<ul class="checks">{li(s["goals"])}</ul>' if s.get('goals') else wait('学習目標')
        history = ''
        if s['past']:
            history = ('<aside class="history-note"><h3>これまでの開催・関連する開催予定</h3><p>' + E(s['past']) +
                       '</p><small>上記は2027年の募集内容とは異なります。今回の条件は開催概要をご確認ください。</small></aside>')
        out += f'''<section id="for-you" class="sec-ivory d-sec"><div class="wrap narrow fade">
  <p class="eyebrow">FOR YOU</p>
  <h2>こんな方におすすめ</h2>
  <ul class="checks">{li(s['for_whom'])}</ul>
  <p class="cond-box"><strong>対象：</strong>{E(s['target'])}<br><strong>受講条件：</strong>{E(s['condition'])}</p>
</div></section>

<section id="goals" class="d-sec"><div class="wrap narrow fade">
  <p class="eyebrow">GOALS</p>
  <h2>学習目標</h2>
  {goals_html}
  <p class="note">※学習目標は講座で扱う範囲を示すものです。技術の習得や施術の効果を保証するものではありません。</p>
</div></section>

<section id="content" class="d-sec" style="padding-top:0"><div class="wrap fade">
  <p class="eyebrow">LECTURE &amp; PRACTICE</p>
  <h2>講義と実技で扱う内容</h2>
  {content_html}
</div></section>

<section id="curriculum" class="sec-charcoal d-sec"><div class="wrap narrow fade">
  <p class="eyebrow">CURRICULUM</p>
  <h2>カリキュラム</h2>
  {cur_html}
</div></section>

<section id="diff" class="d-sec"><div class="wrap narrow fade">
  <p class="eyebrow">DIFFERENCE</p>
  <h2>ほかの零式講座との違い</h2>
  <p>{E(s['diff'])}</p>
  {history}
</div></section>
'''
    certs = '、'.join(c.split('（')[0] for c in INS['certs_private'])
    out += f'''<section id="instructor" class="sec-ivory d-sec"><div class="wrap narrow intro fade">
  <img src="{base}{INS['photo']}" alt="{E(INS['photo_alt'])}" width="440" height="587" loading="lazy">
  <div>
    <p class="eyebrow">INSTRUCTOR</p>
    <p class="name">{E(INS['name'])}</p>
    <p class="role">{E(' ／ '.join(INS['titles']))}<br>{E(INS['job'])}</p>
    <p>民間資格：{E(certs)}。人体解剖実習（5回）、オステオパシー（スラスト BASIC・ADVANCE、内臓調整）を受講。目の前の一人をよく見て、必要なことを、必要な分だけ行う姿勢を、技術と一緒に伝えています。</p>
    <a href="{base}#instructor">講師の詳しいプロフィール</a>
  </div>
</div></section>
'''
    rows = ''.join(f'<tr><th scope="row">{lbl}</th><td>{ov(s, k)}</td></tr>' for k, lbl in OUTLINE_ROWS)
    out += f'''<section id="outline" class="sec-ivory d-sec" style="padding-top:0"><div class="wrap narrow">
  <p class="eyebrow">OUTLINE</p>
  <h2>開催概要</h2>
  <table class="outline">
    <tr><th scope="row">日程</th><td>{E(s['date'])}</td></tr>
    <tr><th scope="row">開催地</th><td>{E(s['place'])}</td></tr>
    <tr><th scope="row">形式</th><td>{E(s['format'])}</td></tr>
    <tr><th scope="row">受講条件</th><td>{E(s['condition'])}</td></tr>
    {rows}
    <tr><th scope="row">受付状況</th><td>{E(status(s))}</td></tr>
  </table>
</div></section>
'''
    if s.get('faq'):
        fq = ''.join(f'<details><summary>{E(q)}</summary><p>{E(a)}</p></details>' for q, a in s['faq'])
        out += f'''<section id="faq" class="d-sec faq"><div class="wrap narrow">
  <p class="eyebrow">FAQ</p>
  <h2>よくある質問</h2>
  {fq}
</div></section>
'''
    rel = [BY[x] for x in s.get('related', []) if x in BY and x != s['slug']][:3]
    rl = ''
    for x in rel:
        note = related_note(s['slug'], x['slug'])
        rl += f'<a href="{base}seminars/{x["slug"]}/"><small>{E(x["date"])}{("｜" + note) if note else ""}</small>{E(x["name"])}</a>'
    tail = '' if can_apply(s) else '。受付開始のご案内を公式LINEでお届けします。'
    out += f'''<section class="sec-charcoal line-cta"><div class="wrap narrow">
  <h2>{E(s['name'])}</h2>
  <p class="lead">対象：{E(s['target'])}／受講条件：{E(s['condition'])}<br>現在の受付状況：{E(status(s))}{tail}</p>
  <div class="btns">{cta_main}<a class="btn" href="{base}#schedule">年間スケジュールに戻る</a></div>
</div>
<div class="wrap" style="margin-top:48px"><h3>関連する講座</h3><div class="related">{rl}</div></div>
</section>
</main>
'''
    sticky_right = cta(s, base) if can_apply(s) else line_button(base, 'LINE受付案内')
    out += foot(base, f'<a class="btn" href="{base}#schedule">年間日程</a>{sticky_right}')
    d = os.path.join(ROOT, 'seminars', s['slug'])
    os.makedirs(d, exist_ok=True)
    open(os.path.join(d, 'index.html'), 'w', encoding='utf-8').write('\n'.join(line.rstrip() for line in out.split('\n')))


if __name__ == '__main__':
    build_index()
    for s in SEMS:
        build_detail(s)
    print('built: index.html +', len(SEMS), 'detail pages')
