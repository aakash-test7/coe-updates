import streamlit as st
import requests
from backend import generate_signed_url, img_to_base64  

# ✅ Cache image fetching and base64 conversion
@st.cache_data(show_spinner=False)
def get_footer_image_base64():
    file_url = generate_signed_url('Logos/mdulogo.png')
    response = requests.get(file_url)
    return img_to_base64(response.content)

# ✅ Footer rendering function
def base_footer():
    img_base64 = get_footer_image_base64()
    footer_image = f"data:image/png;base64,{img_base64}"

    footer = f"""
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        {{position: fixed; bottom: 0; width: 100%;}}

        html, body {{
            width: 100%;
            height: 100%;
            margin: 0;
            padding: 0;
        }}

        body {{
            font-family: 'Poppins', sans-serif;
            background: #eef8ff;
            display: flex;
            flex-direction: column;
            min-height: 100vh;
        }}

        main {{
            flex: 1;
        }}

        .footer-container {{
            width: 100%;
            background: #000;
            color: #fff;
            bottom: 0;
            left: 0;
            padding: 20px 0;
            z-index: 9999;
            border-radius: 15px;
            overflow: hidden;
            display: flex;
            justify-content: space-evenly;
            align-items: flex-start;
            flex-wrap: wrap;
        }}

        .container {{
            width: 100%;
            margin: 0;
            padding: 0 20px;
            display: flex;
            justify-content: space-evenly;
            align-items: flex-start;
            flex-wrap: wrap;
        }}

        .container li a:hover {{
            color: #ffc72c;
            transition: all 0.5s ease;
        }}

        .col-1 {{
            flex-basis: 50%;
            padding: 5px;
        }}

        .col-1 img {{
            width: 55px;
            margin-bottom: 15px;
        }}

        .col-1 p {{
            color: #fff;
            font-size: 16px;
            line-height: 20px;
        }}

        .col-3 {{
            flex-basis: 15%;
            padding: 5px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            text-align: center;
        }}

        .special {{
            color: #fff;
            font-size: 25px;
            margin-top: 10px;
            margin-bottom: 10px;
            font-weight: bold;
        }}

        .col-3 img {{
            min-width: 50%;
        }}

        .container a {{
            color: #fff;
        }}

        .container a:hover {{
            color: #ffc72c;
            transition: all 0.5s ease;
        }}

        .footer-2 {{
            width: 100%;
            background: #2d2d2d;
            color: #fff;
            padding-top: 12px;
            padding-bottom: 2px;
            text-align: center;
        }}

        /* New style for social media links */
        .social-links {{
            display: flex;
            justify-content: flex-end;
            gap: 20px;
            align-items: center;
            color: #fff;
        }}

        .social-links a {{
            text-decoration: none;
            color: #fff;
            display: inline-flex;
            align-items: center;
            font-size: 18px;
            transition: all 0.3s ease;
        }}

        .social-links a:after {{
            content: "→";
            margin-left: 8px;
            font-size: 20px;
            transform: rotate(-45deg);
            transition: all 0.3s ease;
        }}

        .social-links a:hover {{
            text-decoration: underline dotted;
            text-underline-offset: 4px;
            color: #ffffff;
            filter: brightness(1.2);
        }}

        .social-links a:hover:after {{
            transform: rotate(0deg);
            color: #ffffff;
            font-size: 22px;
            margin-left: 10px;
        }}

        /* Special link style (like MDU link) */
        .special {{
            text-decoration: none;
            color: #fff;
            display: inline-flex;
            align-items: center;
            font-size: 25px;
            transition: all 0.3s ease;
        }}

        .special:after {{
            content: "→";
            margin-left: 8px;
            font-size: 28px;
            transform: rotate(-45deg);
            transition: all 0.3s ease;
        }}

        .special:hover {{
            text-decoration: underline dotted;
            text-underline-offset: 4px;
            color: #ffffff;
            filter: brightness(1.2);
        }}

        .special:hover:after {{
            transform: rotate(0deg);
            color: #ffffff;
            font-size: 30px;
            margin-left: 10px;
        }}
    </style>

    <div class="footer-container">
        <div class="container">
            <div class="col-1">
                <p><br><br><br>
                Stress Physiology & Molecular Biology Lab,<br>
                Centre for Biotechnology,<br>
                Maharshi Dayanand University,<br> Rohtak - 124001, Haryana, INDIA<br>
                E-mail: <a href="mailto:ssgill14@mdurohtak.ac.in" style="text-decoration: none;">ssgill14@mdurohtak.ac.in</a><br>
                <a href="mailto:kduiet@mdurohtak.ac.in" style="text-decoration: none; margin-left: 50px; display: inline-block;">kduiet@mdurohtak.ac.in</a><br>
                <a href="mailto:akharbrtk@gmail.com" style="text-decoration: none; margin-left: 50px; display: inline-block;">akharbrtk@gmail.com</a>
                </p>
            </div>
            <div class="col-3">
                <a href="https://mdu.ac.in/default.aspx" class="special" style="text-decoration: none;" target="_blank">MDU</a>
                <img src="{footer_image}" alt="mdu">
            </div>
        </div>
        <div class="social-links">
            <a href="https://www.facebook.com/sharer/sharer.php?u=https://chickpea.mdu.ac.in" target="_blank">Facebook</a>
            <a href="https://twitter.com/intent/tweet?text=Testing%20demo%20for%20social%20media%20reach.%20Hello%20World%20%23science%20%40MDU&url=https://chickpea.mdu.ac.in" target="_blank">Twitter</a>
            <a href="https://www.linkedin.com/feed/?shareActive&mini=true&text=Testing%20demo%20for%20social%20media%20reach.%20Hello%20World%20%23science%20%40MDU%20https%3A%2F%2Fchickpea.mdu.ac.in" target="_blank">LinkedIn</a>
        </div>
        <div class="footer-2">
            <p style="font-size: 15px">Chickpea Omics Explorer</p>
        </div>
    </div>
    """
    st.markdown(footer, unsafe_allow_html=True)
    return
