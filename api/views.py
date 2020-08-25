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
        'Bronze': '30deg, #F49347 20%, #984400 70%, #6E3100 100%',
        'Silver': '30deg, rgb(208, 202, 213) 10%, rgb(107, 126, 145) 70%, rgb(50, 70, 90) 100%',
        'Gold': '30deg, rgb(255, 201, 68) 30%, rgb(222, 130, 34) 100%, rgb(165, 95, 0) 100%',
        'Platinum': '30deg, rgb(140, 197, 132) 40%, rgb(69, 178, 211) 100%, rgb(81, 167, 149) 100%',
        'Diamond': '120deg, rgb(150, 184, 220) 10%, rgb(62, 165, 219) 60%, rgb(77, 99, 153) 100%',
        'Ruby': '30deg, rgb(228, 91, 98) 40%, rgb(214, 28, 86) 100%, rgb(202, 0, 89) 100%'
    }

    api_server = os.environ['API_SERVER']
    boj_handle = request.GET.get("boj", "koosaga")

    user_information_url = api_server + '/user_information.php?id=' + boj_handle
    json = requests.get(user_information_url).json()
    level = json['level']
    solved = '{0:n}'.format(json['solved'])
    boj_class = json['class']
    exp = '{0:n}'.format(json['exp'])
    
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
        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700&display=swap');
        @import url('https://fonts.googleapis.com/css2?family=Caveat:wght@400;700&display=swap');
        :root {{
            background-image: linear-gradient({background_color});
            background-repeat: no-repeat;
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
            text-anchor: "end";
        }}
        ]]>
    </style>
    <line x1="32" y1="60" x2="32" y2="115" stroke-width="2" stroke="white"/>
    <line x1="98" y1="60" x2="98" y2="115" stroke-width="2" stroke="white"/>
    <line x1="32" y1="115" x2="65" y2="135" stroke-width="2" stroke="white"/>
    <line x1="98" y1="115" x2="65" y2="135" stroke-width="2" stroke="white"/>
    <line x1="30" y1="121" x2="65" y2="141" stroke-width="2" stroke="white"/>
    <line x1="98" y1="121" x2="65" y2="141" stroke-width="2" stroke="white"/>
    <text x="145" y="57" class="boj-handle">{boj_handle}</text>
    <text transform="translate(63, 46)" text-anchor="middle" alignment-baseline="middle" class="tier-text">{tier_title}</text>
    <text x="50" y="110" class="tier-number">{tier_rank}</text>
    <text x="145" y="90" class="subtitle">class</text><text x="250" y="90" class="class value">{boj_class}</text>
    <text x="145" y="110" class="subtitle">solved</text><text x="250" y="110" class="solved value">{solved}</text>
    <text x="145" y="130" class="subtitle">exp</text><text x="250" y="130" class="something value">{exp}</text>
    <line x1="0" y1="167" x2="270" y2="167" stroke-width="6" stroke="floralwhite"/>
    <line x1="0" y1="167" x2="350" y2="167" stroke-width="6" stroke-opacity="40%" stroke="floralwhite"/>
</svg>
    '''.format(background_color=BACKGROUND_COLOR[tier_title],
               boj_handle=boj_handle,
               tier_rank=tier_rank,
               tier_title=tier_title,
               solved=solved,
               boj_class=boj_class,
               exp=exp)

    response = HttpResponse(content=svg)
    response['Content-Type'] = 'image/svg+xml'

    return response