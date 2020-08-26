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
        'Unknown': ['#AAAAAA', '#666666', '#000000'],
        'Unrated': ['#666666', '#2D2D2D', '#030202'],
        'Bronze': ['#F49347', '#984400', '#6E3100'],
        'Silver': ['rgb(208, 202, 213)', 'rgb(107, 126, 145)', 'rgb(50, 70, 90)'],
        'Gold': ['rgb(255, 201, 68)', 'rgb(255, 201, 68)', 'rgb(222, 130, 34)'],
        'Platinum': ['rgb(140, 197, 132)', 'rgb(69, 178, 211)', 'rgb(81, 167, 149)'],
        'Diamond': ['rgb(150, 184, 220)', 'rgb(62, 165, 219)', 'rgb(77, 99, 153)'],
        'Ruby': ['rgb(228, 91, 98)', 'rgb(214, 28, 86)', 'rgb(202, 0, 89)']
    }

    api_server = os.environ['API_SERVER']
    boj_handle = request.GET.get("boj", "ccoco")

    user_information_url = api_server + '/v2/users/show.json?id=' + boj_handle

    try:
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
            tier_rank = ''
        else:
            tier_title, tier_rank = TIERS[level].split()
    except KeyError:
        tier_title = "Unknown"
        boj_handle = 'Unknown'
        tier_rank = ''
        solved = '0'
        boj_class = '0'
        exp = '0'
        now_exp = '0'
        needed_exp = '0'
        percentage = '0'
        bar_size = '35'

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
            @keyframes fadeIn {{
                from {{
                    opacity: 0;
                }}
                to {{
                    opacity: 1;
                }}
            }}
            @keyframes expBarAnimation {{
                from {{
                    stroke-dashoffset: {bar_size};
                }}
                to {{
                    stroke-dashoffset: 35;
                }}
            }}
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
                font-weight: 700;
                font-size: 1.45em;
                opacity: 55%;
            }}
            text.tier-number {{
                font-size: 3.1em;
                font-weight: 700;
            }}
            .subtitle {{
                font-weight: 500;
                font-size: 0.9em;
            }}
            .value {{
                font-weight: 400;
                font-size: 0.9em;
            }}
            .percentage {{
                font-weight: 300;
                font-size: 0.8em;
            }}
            .progress {{
                font-size: 0.7em;
            }}
            .item {{
                opacity: 0;
                animation: fadeIn 0.3s ease-in-out forwards;
            }}
            .exp-bar {{
                stroke-dasharray: {bar_size}; 
                stroke-dashoffset: {bar_size};
                animation: expBarAnimation 1s forwards ease-in-out;
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
    <text x="315" y="50" class="tier-text" text-anchor="end" >{tier_title}{tier_rank}</text>
    <text x="35" y="50" class="boj-handle">{boj_handle}</text>
    <g id="this_month_commits" class="item" style="animation-delay: 200ms">
        <text x="35" y="79" class="subtitle">class</text><text x="145" y="79" class="class value">{boj_class}</text>
    </g>
    <g id="this_month_commits" class="item" style="animation-delay: 400ms">
        <text x="35" y="99" class="subtitle">solved</text><text x="145" y="99" class="solved value">{solved}</text>
    </g>
    <g id="this_month_commits" class="item" style="animation-delay: 600ms">
        <text x="35" y="119" class="subtitle">exp</text><text x="145" y="119" class="something value">{exp}</text>
    </g>
    <g id="this_month_commits" class="exp-bar" style="animation-delay: 800ms">
        <line x1="35" y1="142" x2="{bar_size}" y2="142" stroke-width="4" stroke="floralwhite" stroke-linecap="round"/>
    </g>
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
               bar_size=bar_size)

    response = HttpResponse(content=svg)
    response['Content-Type'] = 'image/svg+xml'

    return response
