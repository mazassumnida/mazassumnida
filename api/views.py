import os
import requests
import locale

from django.http import HttpResponse

locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')

# Create your views here.
def generate_badge(request):
    TIERS = (
        "Unrated",
        "Bronze 5",
        "Bronze 4",
        "Bronze 3",
        "Bronze 2",
        "Bronze 1",
        "Silver 5",
        "Silver 4",
        "Silver 3",
        "Silver 2",
        "Silver 1",
        "Gold 5",
        "Gold 4",
        "Gold 3",
        "Gold 2",
        "Gold 1",
        "Platinum 5",
        "Platinum 4",
        "Platinum 3",
        "Platinum 2",
        "Platinum 1",
        "Diamond 5",
        "Diamond 4",
        "Diamond 3",
        "Diamond 2",
        "Diamond 1",
        "Ruby 5",
        "Ruby 4",
        "Ruby 3",
        "Ruby 2",
        "Ruby 1",
    )
    
    BACKGROUND_COLOR = {
        'Unrated': ['#666666', '#2D2D2D', '#030202'],
        'Bronze': ['#F49347', '#984400', '#6E3100'],
        'Silver': ['rgb(208, 202, 213)', 'rgb(107, 126, 145)', 'rgb(50, 70, 90)'],
        'Gold': ['rgb(255, 201, 68)', 'rgb(255, 201, 68)', 'rgb(222, 130, 34)'],
        'Platinum': ['rgb(140, 197, 132)', 'rgb(69, 178, 211)', 'rgb(81, 167, 149)'],
        'Diamond': ['rgb(150, 184, 220)', 'rgb(62, 165, 219)', 'rgb(77, 99, 153)'],
        'Ruby': ['rgb(228, 91, 98)', 'rgb(214, 28, 86)', 'rgb(202, 0, 89)']
    }

    api_server = os.environ['API_SERVER']
    boj_handle = request.GET.get("boj", "koosaga")

    user_information_url = api_server + '/v2/users/show.json?id=' + boj_handle
    json = requests.get(user_information_url).json()
    json = json["result"]['user'][0]
    level = json['level']
    solved = '{0:n}'.format(json['solved'])
    boj_class = json['class']
    
    next_exp = json['next_exp_cap']
    prev_exp = json['previous_exp_cap']
    exp_gap = next_exp - prev_exp
    my_exp = json['exp']
    percentage = round((my_exp - prev_exp) * 100 / exp_gap)
    bar_size = 35 + 2.55 * percentage
    
    needed_exp = '{0:n}'.format(next_exp - prev_exp)
    now_exp = '{0:n}'.format(my_exp - prev_exp)
    exp = '{0:n}'.format(my_exp)
    
    if TIERS[level] == 'Unrated':
        tier_title = TIERS[level]
        tier_rank = 0
    else:
        tier_title, tier_rank = TIERS[level].split()    
    
    svg = '''
    <!DOCTYPE svg PUBLIC 
        "-//W3C//DTD SVG 1.1//EN" 
        "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
<svg height="170" width="350"   
    version="1.1" 
    xmlns="http://www.w3.org/2000/svg" 
    xmlns:xlink="http://www.w3.org/1999/xlink" 
    xml:space="preserve">
    <style type="text/css">
        <![CDATA[
            @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700&display=block');
            @import url('https://fonts.googleapis.com/css2?family=Caveat:wght@400;700&display=block');
            @import url('https://fonts.googleapis.com/css2?family=Baloo+Tamma+2&display=block');
            .background {{
                fill: url(#grad);
            }}
            text {{
                fill: white;
                font-family: 'Noto Sans KR', sans-serif;
            }}
            text.boj-handle {{
                font-weight: 700;
                font-size: 1.45em;
            }}
            text.tier-text {{
                font-family: 'Caveat', cursive;
                font-size: 2em;
            }}
            text.tier-number {{
                font-size: 3.1em;
                font-weight: 700;
            }}
            .subtitle {{
                font-weight: 400;
                font-size: 0.9em;
            }}
            .value {{
                font-weight: 400;
                font-size: 0.9em;
                font-family: 'Baloo Tamma 2', cursive;
            }}
            .percentage {{
                font-weight: 300;
                font-size: 0.8em;
                font-family: 'Baloo Tamma 2', cursive;
            }}
            .progress {{
                font-size: 0.7em;
                font-family: 'Baloo Tamma 2', cursive;
            }}
        ]]>
    </style>
    <defs>
        <linearGradient id="grad" x1="0%" y1="0%" x2="100%" y2="35%">
            <stop offset="10%" style="stop-color:{color1};stop-opacity:1" />
            <stop offset="55%" style="stop-color:{color2};stop-opacity:1" />
            <stop offset="100%" style="stop-color:{color3};stop-opacity:1" />
        </linearGradient>
    </defs>
    <rect width="350" height="170" rx="10" ry="10" class="background"/>
    <line x1="34" y1="50" x2="34" y2="105" stroke-width="2" stroke="white"/>
    <line x1="100" y1="50" x2="100" y2="105" stroke-width="2" stroke="white"/>
    <line x1="34" y1="105" x2="67" y2="125" stroke-width="2" stroke="white"/>
    <line x1="100" y1="105" x2="67" y2="125" stroke-width="2" stroke="white"/>
    <line x1="34" y1="110" x2="67" y2="130" stroke-width="2" stroke="white"/>
    <line x1="100" y1="110" x2="67" y2="130" stroke-width="2" stroke="white"/>
    <text x="145" y="50" class="boj-handle">{boj_handle}</text>
    <text transform="translate(65, 40)" text-anchor="middle" alignment-baseline="middle" class="tier-text">{tier_title}</text>
    <text x="52" y="100" class="tier-number">{tier_rank}</text>
    <text x="145" y="78" class="subtitle">class</text><text x="245" y="78" class="class value">{boj_class}</text>
    <text x="145" y="98" class="subtitle">solved</text><text x="245" y="98" class="solved value">{solved}</text>
    <text x="145" y="118" class="subtitle">exp</text><text x="245" y="118" class="something value">{exp}</text>
    <line x1="35" y1="142" x2="{bar_size}" y2="142" stroke-width="4" stroke="floralwhite" stroke-linecap="round"/>
    <line x1="35" y1="142" x2="290" y2="142" stroke-width="4" stroke-opacity="40%" stroke="floralwhite" stroke-linecap="round"/>
    <text x="297" y="142" alignment-baseline="middle" class="percentage">{percentage}%</text>
    <text x="293" y="157" class="progress" text-anchor="end">{now_exp} / {needed_exp}</text>
</svg>
    '''.format(color1=BACKGROUND_COLOR[tier_title][0],
               color2=BACKGROUND_COLOR[tier_title][1],
               color3=BACKGROUND_COLOR[tier_title][2],
               boj_handle=boj_handle,
               tier_rank=tier_rank,
               tier_title=tier_title,
               solved=solved,
               boj_class=boj_class,
               exp=exp,
               now_exp=now_exp,
               needed_exp=needed_exp,
               percentage=percentage,
               bar_size=bar_size,
               font1=FONT1,
               font2=FONT2)

    response = HttpResponse(content=svg)
    response['Content-Type'] = 'image/svg+xml'

    return response