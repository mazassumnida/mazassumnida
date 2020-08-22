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
    tier = TIERS[json['level']]

    svg = """
    <!DOCTYPE svg PUBLIC 
        "-//W3C//DTD SVG 1.1//EN" 
        "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
    <svg height="60" width="200"   
        version="1.1" 
        xmlns="http://www.w3.org/2000/svg" 
        xmlns:xlink="http://www.w3.org/1999/xlink" 
        xml:space="preserve">
       <text x="0" y="15" fill="red" transform="rotate(30 20,40)">boj : {boj_handle}</text>
       <text x="0" y="15" fill="red" transform="rotate(30 20,40)">tier : {tier}</text>
    </svg>
    """.format(boj_handle=boj_handle, tier=tier)

    response = HttpResponse(content=svg)
    response['Content-Type'] = 'image/svg+xml'

    return response