import os
import requests

from django.http import HttpResponse

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

    api_server = os.environ['API_SERVER']
    boj_handle = request.GET.get("boj", "malkoring")

    user_information_url = api_server + '/user_information.php?id=' + boj_handle
    json = requests.get(user_information_url).json()
    level = json['level']

    tier, limit, *rest = [thres for thres in threshold if level <= thres]
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
            background-image: linear-gradient(30deg, rgb(140, 197, 132) 40%, rgb(69, 178, 211) 100%, rgb(81, 167, 149) 40%);
            background-repeat: no-repeat;
        }}
        text {{
            fill: white;
            font-family: 'Noto Sans KR', sans-serif;
        }}
        text.boj-handle {{
            font-weight: 700;
            font-size: 1.5em;
        }}
        text.tier-text {{
            font-family: 'Caveat', cursive;
            font-size: 2em;
        }}
        text.tier-number {{
            font-size: 3.3em;
            font-weight: 700;
        }}
        .subtitle {{
            font-weight: 300;
            font-size: 0.9em;
        }}
        .value {{
            font-weight: 400;
        }}
        ]]>
    </style>
    <line x1="30" y1="60" x2="30" y2="120" stroke-width="2" stroke="white"/>
    <line x1="100" y1="60" x2="100" y2="120" stroke-width="2" stroke="white"/>
    <line x1="30" y1="120" x2="65" y2="140" stroke-width="2" stroke="white"/>
    <line x1="100" y1="120" x2="65" y2="140" stroke-width="2" stroke="white"/>
    <line x1="30" y1="128" x2="65" y2="148" stroke-width="2" stroke="white"/>
    <line x1="100" y1="128" x2="65" y2="148" stroke-width="2" stroke="white"/>
    <text x="145" y="60" class="boj-handle">{boj_handle}</text>
    <text transform="translate(62, 48)" text-anchor="middle" alignment-baseline="middle" class="tier-text">{tier_title}</text>
    <text x="50" y="115" class="tier-number">{tier_rank}</text>
    <text x="145" y="95" class="subtitle">solved</text><text x="260" y="95" class="solved value">291</text>
    <text x="145" y="115" class="subtitle">class</text><text x="260" y="115" class="class value">3</text>
    <text x="145" y="135" class="subtitle">something</text><text x="260" y="135" class="something value">merong</text>
</svg>
    '''.format(boj_handle=boj_handle, tier_rank=tier_rank, tier_title=tier_title)

    response = HttpResponse(content=svg)
    response['Content-Type'] = 'image/svg+xml'

    return response