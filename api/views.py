import os
import requests
import locale

from django.http import HttpResponse
from .images import UNKNOWN, UNRATED, BRONZE, SILVER, GOLD, PLATINUM, DIAMOND, RUBY

locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')

# Create your views here.
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
    'Unrated': ['#666666', '#2D2D2D', '#040202'],
    'Bronze': ['#F49347', '#984400', '#492000'],
    'Silver': ['#939195', '#6B7E91', '#1F354A'],
    'Gold': ['#FFC944', '#FFAF44', '#FF9632'],
    'Platinum': ['#8CC584', '#45B2D3', '#51A795'],
    'Diamond': ['#96B8DC', '#3EA5DB', '#4D6399', ],
    'Ruby': ['#E45B62', '#E14476', '#CA0059']
}

TIER_IMG_LINK = {
    'Unknown': UNKNOWN,
    'Unrated': UNRATED,
    'Bronze': BRONZE,
    'Silver': SILVER,
    'Gold': GOLD,
    'Platinum': PLATINUM,
    'Diamond': DIAMOND,
    'Ruby': RUBY
}


class Settings_url(object):
    def __init__(self, request, MAX_LEN):
        self.api_server = os.environ['API_SERVER']
        self.boj_handle = request.GET.get("boj", "ccoco")
        if len(self.boj_handle) > MAX_LEN:
            self.boj_name = self.boj_handle[:(MAX_LEN - 2)] + "..."
            print("boj handle edit")
        else:
            self.boj_name = self.boj_handle
        self.user_information_url = self.api_server + \
            '/v2/users/show.json?id=' + self.boj_handle


class Boj_default_settings_try(object):
    def __init__(self, request, url_set):
        try:
            self.json = requests.get(url_set.user_information_url).json()
            self.json = self.json["result"]['user'][0]
            self.level = self.json['level']
            self.solved = '{0:n}'.format(self.json['solved'])
            self.boj_class = self.json['class']

            self.next_exp = self.json['next_exp_cap']
            self.prev_exp = self.json['previous_exp_cap']
            self.exp_gap = self.next_exp - self.prev_exp
            self.my_exp = self.json['exp']
            self.percentage = round(
                (self.my_exp - self.prev_exp) * 100 / self.exp_gap)
            self.bar_size = 35 + 2.55 * self.percentage

            self.needed_exp = '{0:n}'.format(self.next_exp - self.prev_exp)
            self.now_exp = '{0:n}'.format(self.my_exp - self.prev_exp)
            self.exp = '{0:n}'.format(self.my_exp)

            if TIERS[self.level] == 'Unrated':
                self.tier_title = TIERS[self.level]
                self.tier_rank = ''
            else:
                self.tier_title, self.tier_rank = TIERS[self.level].split()
        except KeyError:
            self.tier_title = "Unknown"
            url_set.boj_handle = 'Unknown'
            self.tier_rank = ''
            self.solved = '0'
            self.boj_class = '0'
            self.exp = '0'
            self.now_exp = '0'
            self.needed_exp = '0'
            self.percentage = '0'
            self.bar_size = '35'


def generate_badge(request):
    MAX_LEN = 11
    url_set = Settings_url(request, MAX_LEN)
    handle_set = Boj_default_settings_try(request, url_set, )

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
            @keyframes delayFadeIn {{
                0%{{
                    opacity:0
                }}
                60%{{
                    opacity:0
                }}
                100%{{
                    opacity:1
                }}           
            }}
            @keyframes fadeIn {{
                from {{
                    opacity: 0;
                }}
                to {{
                    opacity: 1;
                }}
            }}
            @keyframes expBarAnimation {{
                0% {{
                    stroke-dashoffset: {bar_size};
                }}
                70% {{
                    stroke-dashoffset: {bar_size};
                }}
                100%{{
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
                animation: fadeIn 0.8s ease-in-out forwards;
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
                animation: delayFadeIn 1s ease-in-out forwards;
            }}
            .exp-bar {{
                stroke-dasharray: {bar_size}; 
                stroke-dashoffset: {bar_size};
                animation: expBarAnimation 1.5s forwards ease-in-out;
            }}
        ]]>
    </style>
    <defs>
        <linearGradient id="grad" x1="0%" y1="0%" x2="100%" y2="35%">
            <stop offset="10%" style="stop-color:{color1};stop-opacity:1"></stop>
            <stop offset="55%" style="stop-color:{color2};stop-opacity:1"></stop>
            <stop offset="100%" style="stop-color:{color3};stop-opacity:1"></stop>
        </linearGradient>
    </defs>
    <rect width="350" height="170" rx="10" ry="10" class="background"/>
    <text x="315" y="50" class="tier-text" text-anchor="end" >{tier_title}{tier_rank}</text>
    <text x="35" y="50" class="boj-handle">{boj_handle}</text>
    <g class="item" style="animation-delay: 200ms">
        <text x="35" y="79" class="subtitle">class</text><text x="145" y="79" class="class value">{boj_class}</text>
    </g>
    <g class="item" style="animation-delay: 400ms">
        <text x="35" y="99" class="subtitle">solved</text><text x="145" y="99" class="solved value">{solved}</text>
    </g>
    <g class="item" style="animation-delay: 600ms">
        <text x="35" y="119" class="subtitle">exp</text><text x="145" y="119" class="something value">{exp}</text>
    </g>
    <g class="exp-bar" style="animation-delay: 800ms">
        <line x1="35" y1="142" x2="{bar_size}" y2="142" stroke-width="4" stroke="floralwhite" stroke-linecap="round"/>
    </g>
    <line x1="35" y1="142" x2="290" y2="142" stroke-width="4" stroke-opacity="40%" stroke="floralwhite" stroke-linecap="round"/>
    <text x="297" y="142" alignment-baseline="middle" class="percentage">{percentage}%</text>
    <text x="293" y="157" class="progress" text-anchor="end">{now_exp} / {needed_exp}</text>
</svg>
    '''.format(color1=BACKGROUND_COLOR[handle_set.tier_title][0],
               color2=BACKGROUND_COLOR[handle_set.tier_title][1],
               color3=BACKGROUND_COLOR[handle_set.tier_title][2],
               boj_handle=url_set.boj_name,
               tier_rank=handle_set.tier_rank,
               tier_title=handle_set.tier_title,
               solved=handle_set.solved,
               boj_class=handle_set.boj_class,
               exp=handle_set.exp,
               now_exp=handle_set.now_exp,
               needed_exp=handle_set.needed_exp,
               percentage=handle_set.percentage,
               bar_size=handle_set.bar_size)

    response = HttpResponse(content=svg)
    response['Content-Type'] = 'image/svg+xml'

    return response


def generate_badge_v2(request):
    MAX_LEN = 15
    url_set = Settings_url(request, MAX_LEN)
    handle_set = Boj_default_settings_try(request, url_set)

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
                0%{{
                    opacity:0
                }}
                100%{{
                    opacity:1
                }}
            }}
            @keyframes delayFadeIn {{
                0%{{
                    opacity:0
                }}
                80%{{
                    opacity:0
                }}
                100%{{
                    opacity:1
                }}           
            }}
            @keyframes expBarAnimation {{
                0% {{
                    stroke-dashoffset: {bar_size};
                }}
                70% {{
                    stroke-dashoffset: {bar_size};
                }}
                100%{{
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
                font-size: 1.30em;
                animation: fadeIn 1s ease-in-out forwards;

            }}
            text.tier-text {{
                font-weight: 700;
                font-size: 1.45em;
                opacity: 55%;
            }}
            text.tier-number {{
                font-size: 3.1em;
                font-weight: 700;
                animation: delayFadeIn 2s ease-in-out forwards;
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
                animation: delayFadeIn 2s ease-in-out forwards;
            }}
            .exp-bar {{
                stroke-dasharray: {bar_size}; 
                stroke-dashoffset: {bar_size};
                animation: expBarAnimation 1.5s forwards ease-in-out;
            }}
            .tier-title {{
                animation: delayFadeIn 2s ease-in-out forwards;
            }}
        ]]>
    </style>
    <defs>
        <linearGradient id="grad" x1="0%" y1="0%" x2="100%" y2="35%">
           <stop offset="10%" style="stop-color:{color1};stop-opacity:1">
                <animate attributeName="stop-opacity" values="0.7; 0.73; 0.9 ; 0.97; 1; 0.97; 0.9; 0.73; 0.7;" dur="4s" repeatCount="indefinite" repeatDur="01:00"></animate>
            </stop>
            <stop offset="55%" style="stop-color:{color2};stop-opacity:1">
                <animate attributeName="stop-opacity" values="1; 0.95; 0.93; 0.95; 1;" dur="4s" repeatCount="indefinite" repeatDur="01:00"></animate>
            </stop>
            <stop offset="100%" style="stop-color:{color3};stop-opacity:1">
                <animate attributeName="stop-opacity" values="1; 0.97; 0.9; 0.83; 0.8; 0.83; 0.9; 0.97; 1;" dur="4s" repeatCount="indefinite" repeatDur="01:00"></animate>
            </stop>
        </linearGradient>
    </defs>
    <rect width="350" height="170" rx="10" ry="10" class="background"/>
    <line x1="34" y1="50" x2="34" y2="50" stroke-width="2" stroke="white">
        <animate attributeName="y2" from="50" to="105" begin="0.5s" dur="0.3s" fill="freeze"
        calcMode="spline" keyTimes="0 ; 0.25 ; 0.5 ; 0.75 ; 1"
        keySplines="0.5 0 0.5 1 ; 0.5 0 0.5 1 ; 0.5 0 0.5 1 ; 0.5 0 0.5 1" /> 
    </line>
    <line x1="34" y1="105" x2="34" y2="105" stroke-width="2" stroke="white">
        <animate attributeName="x2" from="34" to="67" begin="0.8s" dur="0.2s" fill="freeze" 
        calcMode="spline" keyTimes="0 ; 0.25 ; 0.5 ; 0.75 ; 1"
        keySplines="0.5 0 0.5 1 ; 0.5 0 0.5 1 ; 0.5 0 0.5 1 ; 0.5 0 0.5 1"/> 
        <animate attributeName="y2" from="105" to="125" begin="0.8s" dur="0.2s" fill="freeze" 
        calcMode="spline" keyTimes="0 ; 0.25 ; 0.5 ; 0.75 ; 1"
        keySplines="0.5 0 0.5 1 ; 0.5 0 0.5 1 ; 0.5 0 0.5 1 ; 0.5 0 0.5 1"/> 
    </line>
    <line x1="67" y1="125" x2="67" y2="125" stroke-width="2" stroke="white">
        <animate attributeName="x2" from="67" to="100" begin="1s" dur="0.2s" fill="freeze" 
        calcMode="spline" keyTimes="0 ; 0.25 ; 0.5 ; 0.75 ; 1"
        keySplines="0.5 0 0.5 1 ; 0.5 0 0.5 1 ; 0.5 0 0.5 1 ; 0.5 0 0.5 1"/> 
        <animate attributeName="y2" from="125" to="105" begin="1s" dur="0.2s" fill="freeze" 
        calcMode="spline" keyTimes="0 ; 0.25 ; 0.5 ; 0.75 ; 1"
        keySplines="0.5 0 0.5 1 ; 0.5 0 0.5 1 ; 0.5 0 0.5 1 ; 0.5 0 0.5 1"/> 
    </line>
    <line x1="100" y1="105" x2="100" y2="105" stroke-width="2" stroke="white">
        <animate attributeName="y2" from="105" to="50" begin="1.2s" dur="0.3s" fill="freeze" 
        calcMode="spline" keyTimes="0 ; 0.25 ; 0.5 ; 0.75 ; 1"
        keySplines="0.5 0 0.5 1 ; 0.5 0 0.5 1 ; 0.5 0 0.5 1 ; 0.5 0 0.5 1"/> 
    </line>

    <line x1="67" y1="130" x2="67" y2="130" stroke-width="2" stroke="white">
        <animate attributeName="x2" from="67" to="34" begin="1.5s" dur="0.4s" fill="freeze" 
        calcMode="spline" keyTimes="0 ; 0.25 ; 0.5 ; 0.75 ; 1"
        keySplines="0.5 0 0.5 1 ; 0.5 0 0.5 1 ; 0.5 0 0.5 1 ; 0.5 0 0.5 1" /> 
        <animate attributeName="y2" from="130" to="110" begin="1.5s" dur="0.4s" fill="freeze" 
        calcMode="spline" keyTimes="0 ; 0.25 ; 0.5 ; 0.75 ; 1"
        keySplines="0.5 0 0.5 1 ; 0.5 0 0.5 1 ; 0.5 0 0.5 1 ; 0.5 0 0.5 1" /> 
    </line>

    <line x1="67" y1="130" x2="67" y2="130" stroke-width="2" stroke="white">
        <animate attributeName="x2" from="67" to="100" begin="1.5s" dur="0.4s" fill="freeze"
        calcMode="spline" keyTimes="0 ; 0.25 ; 0.5 ; 0.75 ; 1"
        keySplines="0.5 0 0.5 1 ; 0.5 0 0.5 1 ; 0.5 0 0.5 1 ; 0.5 0 0.5 1"/> 
        <animate attributeName="y2" from="130" to="110" begin="1.5s" dur="0.4s" fill="freeze"
        calcMode="spline" keyTimes="0 ; 0.25 ; 0.5 ; 0.75 ; 1"
        keySplines="0.5 0 0.5 1 ; 0.5 0 0.5 1 ; 0.5 0 0.5 1 ; 0.5 0 0.5 1"/> 
    </line>

    <text x="135" y="50" class="boj-handle">{boj_handle}</text>
    <image href="{tier_img_link}" x="18" y="12" height="50px" width="100px" class="tier-title"/>
    <text x="52" y="100" class="tier-number">{tier_rank}</text>
    <g class="item" style="animation-delay: 200ms">
        <text x="135" y="79" class="subtitle">class</text><text x="225" y="79" class="class value">{boj_class}</text>
    </g>
    <g class="item" style="animation-delay: 400ms">
        <text x="135" y="99" class="subtitle">solved</text><text x="225" y="99" class="solved value">{solved}</text>
    </g>
    <g class="item" style="animation-delay: 600ms">
        <text x="135" y="119" class="subtitle">exp</text><text x="225" y="119" class="something value">{exp}</text>
    </g>
    <g class="exp-bar" style="animation-delay: 800ms">
        <line x1="35" y1="142" x2="{bar_size}" y2="142" stroke-width="4" stroke="floralwhite" stroke-linecap="round"/>
    </g>
    <line x1="35" y1="142" x2="290" y2="142" stroke-width="4" stroke-opacity="40%" stroke="floralwhite" stroke-linecap="round"/>
    <text x="297" y="142" alignment-baseline="middle" class="percentage">{percentage}%</text>
    <text x="293" y="157" class="progress" text-anchor="end">{now_exp} / {needed_exp}</text>
</svg>
    '''.format(color1=BACKGROUND_COLOR[handle_set.tier_title][0],
               color2=BACKGROUND_COLOR[handle_set.tier_title][1],
               color3=BACKGROUND_COLOR[handle_set.tier_title][2],
               boj_handle=url_set.boj_name,
               tier_rank=handle_set.tier_rank,
               tier_img_link=TIER_IMG_LINK[handle_set.tier_title],
               solved=handle_set.solved,
               boj_class=handle_set.boj_class,
               exp=handle_set.exp,
               now_exp=handle_set.now_exp,
               needed_exp=handle_set.needed_exp,
               percentage=handle_set.percentage,
               bar_size=handle_set.bar_size)

    response = HttpResponse(content=svg)
    response['Content-Type'] = 'image/svg+xml'

    return response
