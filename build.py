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

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA = json.load(open(os.path.join(ROOT, 'data', 'seminars.json'), encoding='utf-8'))
SITE, INS, SEMS = DATA['site'], DATA['instructor'], DATA['seminars']
BY = {s['slug']: s for s in SEMS}
RELEASE_OF = {slug: r for r in SITE['release'] for slug in r['slugs']}
E = html.escape


def status(s):
    r = RELEASE_OF[s['slug']]
    return f"受付前（{r['month']}受付開始予定）"


def line_button(base, label='公式LINEで受付案内を受け取る', cls='btn solid'):
    if SITE['line_url']:
        return f'<a class="{cls}" href="{E(SITE["line_url"])}" rel="noopener">{label}</a>'
    return f'<span class="btn disabled" aria-disabled="true">{label}<small style="font-size:.75em">（準備中）</small></span>'


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
<link rel="stylesheet" href="{base}assets/style.css">
<script src="{base}assets/main.js" defer></script>
</head>
<body class="has-sticky">
<a class="skip" href="#main">本文へ移動</a>
<header class="site-header"><div class="wrap">
  <a class="brand" href="{base}">ZERO<small>零式 2027 年間セミナー</small></a>
  <nav class="nav" aria-label="サイト内">
    <a href="{base}#schedule">年間スケジュール</a><a href="{base}#instructor">講師</a><a href="{base}#seminars">セミナー一覧</a><a href="{base}#entry">受付・申込</a>
  </nav>
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
    return f'''<article class="card fade">
  <img src="{base}{s['image']}" alt="{E(s['image_alt'])}" loading="lazy" width="800" height="500">
  <div class="card-body">
    <div class="lv">{E(s['level'])}</div>
    <h3>{E(s['name'])}</h3>
    <a class="btn" href="{url}" aria-label="{E(s['name'])}のセミナー詳細を見る">セミナー詳細を見る</a>
    <p>{E(s['summary'])}</p>
    <dl>
      <dt>日程</dt><dd>{E(s['date'])}</dd>
      <dt>会場</dt><dd>{E(s['place'])}</dd>
      <dt>形式</dt><dd>{E(s['format'])}</dd>
      <dt>対象</dt><dd>{E(s['target'])}</dd>
      <dt>受講条件</dt><dd>{E(s['condition'])}</dd>
      <dt>受付</dt><dd>{E(status(s))}</dd>
    </dl>
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
      <li>土日開催</li>
    </ul>
    <div class="btns">
      <a class="btn solid" href="#schedule">年間スケジュールを見る</a>
      <a class="btn" href="#seminars">セミナー一覧を見る</a>
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
    <p class="lead">零式の講座は、入門から統合までの段階に分かれています。<span class="mk">受講条件のない講座</span>から学びはじめ、条件のある講座へ順に進めます。</p>
    <div class="steps">
      <div class="step fade"><div class="lv">STEP 1｜入門</div><h3>手・足をつくる</h3><p>零式-「手」を作るセミナー／零式-足を作るセミナー。受講条件なし。</p></div>
      <div class="step fade"><div class="lv">STEP 2｜基幹</div><h3>零式-ヘッドコンディショニング極</h3><p>零式の中心となる技術。受講条件なし。</p></div>
      <div class="step fade"><div class="lv">STEP 3｜応用・上位</div><h3>姿勢・経絡・関節・内臓</h3><p>美姿勢、経絡ストレッチ、関節調整法、内臓調整など。関節調整法ADVANCEはBASIC修了者が対象。</p></div>
      <div class="step fade"><div class="lv">STEP 4｜統合</div><h3>ZERO RECOVERY</h3><p>零式の技術を統合する最上位講座。零式-ヘッドコンディショニング極の修了者が対象。</p></div>
    </div>
    <p class="cond">受講条件のある講座：零式-関節調整法 ADVANCE（BASIC修了者）／零式-ZERO RECOVERY 第2期（零式-ヘッドコンディショニング極の修了者）</p>
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
    <p class="lead">各講座の内容・対象・受講条件は、詳細ページでご確認いただけます。</p>
    <div class="cards">
{cards}
    </div>
    <p class="note">※料金・定員・会場・時間は、各講座の受付開始時にご案内します。</p>
  </div>
</section>

<section id="entry" class="sec-ivory">
  <div class="wrap">
    <p class="eyebrow">ENTRY</p>
    <h2>受付開始時期と、お申し込みの流れ</h2>
    <p class="lead">受付は年4回、開催時期ごとに開始します（2026年11月・2027年1月・4月・7月）。受付開始のお知らせは公式LINEでお届けします。</p>
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
    <p class="lead">現在、2027年の講座はすべて受付前です。受付開始のご案内を公式LINEでお届けします。</p>
    <div class="btns">{line_button(base)}</div>
  </div>
</section>
</main>
'''
    out += foot(base, f'<a class="btn" href="#schedule">年間日程</a>{line_button(base, "LINE受付案内")}')
    open(os.path.join(ROOT, 'index.html'), 'w', encoding='utf-8').write(out)


def build_detail(s):
    base = '../../'
    url_self = f'{base}seminars/{s["slug"]}/'
    pending = s.get('pending')
    li = lambda xs: ''.join(f'<li>{E(x)}</li>' for x in xs)
    title = f'{s["name"]}｜零式 2027 年間セミナー'
    desc = f'{s["name"]}（{s["date"]}・{s["place"]}）。{s["summary"]}'
    out = head(title, desc, base)
    cta_main = line_button(base)
    out += f'''<main id="main">
<div class="wrap crumb"><a href="{base}">トップ</a> ／ <a href="{base}#seminars">セミナー一覧</a> ／ {E(s['name'])}</div>
<div class="wrap d-hero">
  <div>
    <p class="eyebrow">{E(s['level'])}｜{s['month']}月開催</p>
    <h1>{E(s['name'])}</h1>
    <p class="catch">{E(s['catch'])}</p>
    <p>{E(s['summary'])}</p>
    <dl class="facts">
      <dt>日程</dt><dd>{E(s['date'])}</dd>
      <dt>会場</dt><dd>{E(s['place'])}{'（詳細は受付開始時にご案内）' if not pending else ''}</dd>
      <dt>形式</dt><dd>{E(s['format'])}</dd>
      <dt>対象</dt><dd>{E(s['target'])}</dd>
      <dt>受講条件</dt><dd>{E(s['condition'])}</dd>
      <dt>受付状況</dt><dd>{E(status(s))}</dd>
    </dl>
    <div class="btns">{cta_main}<a class="btn" href="{base}#schedule">年間スケジュールに戻る</a></div>
  </div>
  <img src="{base}{s['image']}" alt="{E(s['image_alt'])}" width="800" height="600">
</div>
'''
    if pending:
        out += f'''<section class="sec-ivory d-sec"><div class="wrap narrow">
  <h2>講座内容は詳細準備中です</h2>
  <div class="pending-box">2027年11月13日（土）に東京で開催を予定しています。講座名・内容・対象・受講条件は決まり次第、公式LINEとこのページでお知らせします。</div>
</div></section>
'''
    else:
        out += f'''<section class="sec-ivory d-sec"><div class="wrap narrow fade">
  <p class="eyebrow">FOR YOU</p>
  <h2>こんな方におすすめ</h2>
  <ul class="checks">{li(s['for_whom'])}</ul>
  <p style="margin-top:20px"><strong>対象：</strong>{E(s['target'])}<br><strong>受講条件：</strong>{E(s['condition'])}</p>
</div></section>

<section class="d-sec"><div class="wrap narrow fade">
  <p class="eyebrow">WHAT YOU LEARN</p>
  <h2>このセミナーで学ぶこと</h2>
  <ul class="checks">{li(s['learn'])}</ul>
  <h3 style="margin:32px 0 10px">ほかの講座との違い</h3>
  <p>{E(s['diff'])}</p>
</div></section>

<section class="sec-charcoal d-sec"><div class="wrap narrow fade">
  <p class="eyebrow">CURRICULUM</p>
  <h2>カリキュラム</h2>
  <div class="pending-box">講義と実技の順序・{'日別の内容・' if '2日' in s['format'] or '3日' in s['format'] else ''}時間割は、受付開始時にこのページでご案内します。</div>
</div></section>

<section class="d-sec"><div class="wrap fade">
  <p class="eyebrow">ATMOSPHERE</p>
  <h2>講習の雰囲気</h2>
  <p class="lead">講師の実演を間近で見ながら、考え方と手技を学びます。{E(s['past'])}</p>
  <div class="mood">
    <img src="{base}images/practice-leg.jpg" alt="ベッド上の受講者の足で実演する原口慶篤と、見学する受講者たち" loading="lazy" width="800" height="800">
    <img src="{base}images/practice-arm.jpg" alt="受講者の前腕に触れながら説明する原口慶篤" loading="lazy" width="800" height="800">
    <img src="{base}images/lecture-skeleton.jpg" alt="骨格模型で説明する原口慶篤" loading="lazy" width="800" height="800">
  </div>
  <p class="note">※写真は過去の零式セミナーの様子です。</p>
</div></section>
'''
    out += f'''<section class="sec-ivory d-sec"><div class="wrap narrow intro fade">
  <img src="{base}{INS['photo']}" alt="{E(INS['photo_alt'])}" width="440" height="587" loading="lazy">
  <div>
    <p class="eyebrow">INSTRUCTOR</p>
    <p class="name">{E(INS['name'])}</p>
    <p class="role">{E(' ／ '.join(INS['titles']))}<br>{E(INS['job'])}</p>
    <p>民間資格：{E('、'.join(c.split('（')[0] for c in INS['certs_private']))}。人体解剖実習（5回）、オステオパシー（スラスト BASIC・ADVANCE、内臓調整）を受講。目の前の一人をよく見て、必要なことを、必要な分だけ行う姿勢を、技術と一緒に伝えています。</p>
    <a href="{base}#instructor">講師の詳しいプロフィール</a>
  </div>
</div></section>

<section class="sec-ivory d-sec" style="padding-top:0"><div class="wrap narrow">
  <p class="eyebrow">OUTLINE</p>
  <h2>開催概要</h2>
  <table class="outline">
    <tr><th scope="row">日程</th><td>{E(s['date'])}</td></tr>
    <tr><th scope="row">時間</th><td>受付開始時にご案内します</td></tr>
    <tr><th scope="row">会場・アクセス</th><td>{E(s['place'])}（詳細は受付開始時にご案内します）</td></tr>
    <tr><th scope="row">形式</th><td>{E(s['format'])}</td></tr>
    <tr><th scope="row">受講料</th><td>受付開始時にご案内します（税込・税別の区別も併せて表示します）</td></tr>
    <tr><th scope="row">定員</th><td>受付開始時にご案内します</td></tr>
    <tr><th scope="row">持ち物</th><td>受付開始時にご案内します</td></tr>
    <tr><th scope="row">受講条件</th><td>{E(s['condition'])}</td></tr>
    <tr><th scope="row">申込期限</th><td>受付開始時にご案内します</td></tr>
    <tr><th scope="row">支払い方法</th><td>受付開始時にご案内します</td></tr>
    <tr><th scope="row">キャンセル条件</th><td>お申し込み前に規約でご案内します</td></tr>
    <tr><th scope="row">受付状況</th><td>{E(status(s))}</td></tr>
  </table>
</div></section>
'''
    if s.get('faq'):
        fq = ''.join(f'<details><summary>{E(q)}</summary><p>{E(a)}</p></details>' for q, a in s['faq'])
        out += f'''<section class="d-sec faq"><div class="wrap narrow">
  <p class="eyebrow">FAQ</p>
  <h2>よくある質問</h2>
  {fq}
</div></section>
'''
    idx = SEMS.index(s)
    rel = [x for x in (SEMS[idx - 1] if idx > 0 else None, SEMS[idx + 1] if idx + 1 < len(SEMS) else None) if x]
    if s['slug'] == 'kansetsu-basic':
        rel = [BY['kansetsu-advance']] + rel
    if s['slug'] == 'kansetsu-advance':
        rel = [BY['kansetsu-basic']] + rel
    if s['slug'] == 'zero-recovery':
        rel = [BY['kiwami']] + rel
    seen, rel_u = set(), []
    for x in rel:
        if x['slug'] not in seen and x['slug'] != s['slug']:
            seen.add(x['slug']); rel_u.append(x)
    rl = ''.join(f'<a href="{base}seminars/{x["slug"]}/"><small>{E(x["date"])}</small>{E(x["name"])}</a>' for x in rel_u[:3])
    out += f'''<section class="sec-charcoal line-cta"><div class="wrap narrow">
  <h2>{E(s['name'])}</h2>
  <p class="lead">対象：{E(s['target'])}／受講条件：{E(s['condition'])}<br>この講座は{E(status(s))}です。受付開始のご案内を公式LINEでお届けします。</p>
  <div class="btns">{cta_main}<a class="btn" href="{base}#schedule">年間スケジュールに戻る</a></div>
</div>
<div class="wrap" style="margin-top:48px"><h3>関連する講座</h3><div class="related">{rl}</div></div>
</section>
</main>
'''
    out += foot(base, f'<a class="btn" href="{base}#schedule">年間日程</a>{line_button(base, "LINE受付案内")}')
    d = os.path.join(ROOT, 'seminars', s['slug'])
    os.makedirs(d, exist_ok=True)
    open(os.path.join(d, 'index.html'), 'w', encoding='utf-8').write(out)


if __name__ == '__main__':
    build_index()
    for s in SEMS:
        build_detail(s)
    print('built: index.html +', len(SEMS), 'detail pages')
