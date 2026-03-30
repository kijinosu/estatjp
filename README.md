# estatjp

[![image](https://zenodo.org/badge/DOI/10.5281/zenodo.19124885.svg)](https://doi.org/10.5281/zenodo.19124885)

[![Copier](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/copier-org/copier/master/img/badge/badge-grayscale-inverted-border-teal.json)](https://github.com/copier-org/copier)

[E-Stat](https://www.e-stat.go.jp/en) is a widely used portal site for
accessing Japanese governmental statistical data. Began operation in
2008. e-Stat currently hosts [744 surveys (1,688,550 datasets) in
Japanese](https://www.e-stat.go.jp/stat-search?page=1) from about 30
governmental agencies with [56 surveys (292,856 datasets) available in
English](https://www.e-stat.go.jp/en/stat-search?page=1). These
collections contain 'databases' and files (mainly Excel files). The
'databases' can be accessed via an API. API urls can cover entire
databases or subsets that can be tailored to users' individual needs.

The objective of the estatjp Python package is to provide access to the
e-Stat portal and return datasets in pandas.DataFrame format.

For example, the e-Stat API returns CSV streams that contain headers
with metadata. These headers interfere with pandas.get_csv. The first
release of estatjp returns a dictionary that contains the header and
main table as separate dataframes.

## Requirement

The e-Stat API requires an application ID that can be obtained from the
[E-Stat API](https://www.e-stat.go.jp/api/en) page. Install this ID into
your project by setting your terminal to your project root and running
the following commands:

    pip install python-dotenv
    dotenv set ESTAT_APP_ID your-app-id

## Install this package

    pip install estatjp

## Example

This example downloads an English dataset, the [Labour Force Survey
Basic Tabulation Whole Japan Monthly table Population of 15 years old
and over by labour force
status](https://www.e-stat.go.jp/en/dbview?sid=0003005798). The API url
for that table is assigned to enurl below.

``` python
import pandas
from dotenv import load_dotenv
from estatjp import api
enurl = 'http://api.e-stat.go.jp/rest/3.0/app/getSimpleStatsData?appId=&lang=E&statsDataId=0003005798&metaGetFlg=Y&cntGetFlg=N&explanationGetFlg=Y&annotationGetFlg=Y&sectionHeaderFlg=1&replaceSpChars=0'
dfs = api.get_csv_data(enurl)
print(dfs.get('Header'))
print(dfs.get('Main'))
print(dfs.get('Description'))
```

### References

<div id="refs" class="container references csl-bib-body hanging-indent">

<div id="ref-ashizawa2022estat.en" class="container csl-entry">

Ashikawa, Souta, Matsuda, Junichi, & Osone, Tadashi. (2022). Method for
improving the recall in e-stat data search. *Proceedings of Annual
Conference of the Information Systems Society in Japan ISSJ2022*, S1–C1.
<https://doi.org/10.19014/proceedingsissj.18.0_S1-C1>

</div>

<div id="ref-ashizawa2023estat.en" class="container csl-entry">

Ashikawa, Souta, Matsuda, Junichi, & Osone, Tadashi. (2023). Development
of front-end search system improving recall in e-stat. *Proceedings of
Annual Conference of the Information Systems Society in Japan ISSJ2023*,
1–6. <https://doi.org/10.19014/proceedingsissj.19.0_P001>

</div>

<div id="ref-cocosan2023python.en" class="container csl-entry">

cocosan. (2023). *Python apuri: Seifu tokei e-stat wo shigoto ni ikase!*
<https://www.youtube.com/watch?v=hiaK-jTXpCI>.

</div>

<div id="ref-higashi2024incidence" class="container csl-entry">

Higashi, Takahiro, & Kurokawa, Yukinori. (2024). Incidence, mortality,
survival, and treatment statistics of cancers in digestive
organs—japanese cancer statistics 2024. *Annals of Gastroenterological
Surgery*, *8*(6), 958–965. <https://doi.org/10.1002/ags3.12835>

</div>

<div id="ref-inoue2023self" class="container csl-entry">

Inoue, Takao. (2023). A self-made tutorial for GitHub flavored markdown
(GFM), and its source codes. *ResearchGate*.
<https://www.researchgate.net/publication/370937551_A_self-made_tutorial_for_GitHub_Flavored_Markdown_GFM_and_its_source_codes>

</div>

<div id="ref-kato2021residential" class="container csl-entry">

Kato, Haruka, & Takizawa, Atsushi. (2021). Which residential clusters of
walkability affect future population from the perspective of real estate
prices in the osaka metropolitan area? *Sustainability*, *13*(23),
13413. <https://doi.org/10.3390/su132313413>

</div>

<div id="ref-masui2021r.en" class="container csl-entry">

Masui, Toshikatsu. (2021). *R to python de manabu tokeigaku nyumon*.
Ohmsha.

</div>

<div id="ref-estat2016adaptor" class="container csl-entry">

National Statistics Center, Japan. (2016). *Chukan apuri*.
<https://github.com/e-stat-api/adaptor>.

</div>

<div id="ref-nishimura2017linked.en" class="container csl-entry">

Nishimura, Shoki. (2017). Providing statistical data by linked open data
(LOD): Innovative official statistical data (e-stat) dissemination.
*Joho Kanri*, *59*(12), 812–821.
<https://doi.org/10.1241/johokanri.59.812>

</div>

<div id="ref-seki2023social" class="container csl-entry">

Seki, Katsunori. (2023). Social identification and redistribution
preference: A survey experiment in japan. *Social Science Japan
Journal*, *26*(1), 47–60. <https://doi.org/10.1093/ssjj/jyac029>

</div>

<div id="ref-takahashi2022estat.en" class="container csl-entry">

Takahashi, Shūichiro. (2022). *E-stat to nakayokusuru hon: Python to
ōpun deta de nihon wo bunseki suru! API keiyu de seifu tōkei wo shutoku!
katsuyo!* Impress R&D.

</div>

<div id="ref-wakabayashi2015public.en" class="container csl-entry">

Wakabayashi, Chihiro, Shinmura, Hiromi, Ando, Miri, Shimada, Masako, &
Yanagawa, Hiroshi. (2015). Kōeisei topikksu dai 13 kai seifutōkei no
sōgōmadoguchi e-stat: Chiiki shindan he no katsuyō - jissen herusu
puromōshon. *Gekkan Chiiki Igaku*, *29*(2), 52.
<https://doi.org/10.60261/chiikiigaku.29.2_52>

</div>

<div id="ref-ashizawa2022estat.ja" class="container csl-entry">

芦澤颯太, 松田純一, & 大曽根匡. (2022). E-stat
での統計データ検索におけるいくつかの課題抽出とその解決方法の提案.
*情報システム学会 全国大会論文集 ISSJ2022*, S1–C1.
<https://doi.org/10.19014/proceedingsissj.18.0_S1-C1>

</div>

<div id="ref-ashizawa2023estat.ja" class="container csl-entry">

芦澤颯太, 松田純一, & 大曽根匡. (2023). E-stat
における検索漏れを抑止する情報システムの開発とその検証.
*情報システム学会 全国大会論文集 情報システム学会*, 1–6.
<https://doi.org/10.19014/proceedingsissj.19.0_P001>

</div>

<div id="ref-wakabayashi2015public.ja" class="container csl-entry">

若林チヒロ, 新村洋未, 安藤実里, 嶋田雅子, & 柳川洋. (2015).
公衆衛生トピックス 第 13 回 政府統計の総合窓口
e-stat-地域診断への活用-実践ヘルスプロモーション. *月刊地域医学*,
*29*(2), 52. <https://doi.org/10.60261/chiikiigaku.29.2_52>

</div>

<div id="ref-nishimura2017linked.ja" class="container csl-entry">

西村正貴. (2017). Linked open data (LOD) による統計データの提供:
政府統計データ (e-stat) の新しい形. *情報管理*, *59*(12), 812–821.
<https://doi.org/10.1241/johokanri.59.812>

</div>

</div>
