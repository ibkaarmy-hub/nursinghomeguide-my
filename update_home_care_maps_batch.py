"""
Update 21 home-care facilities with Google Maps scraper data.
Sources: Apify compass/crawler-google-places run qwjq5gKahMIk3e4v2
Dataset: sJpmtkOpdWuJKOfSM
"""

import csv, json, urllib.request, time, re, sys, io
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

SHEET_ID = '1HpAXH9aG1O27Cvhfu4MIOa9sRYhwIL4C_WUoFfC-9qk'
SHEET_TAB = 'google-sheets-facilities.csv'
TOKEN_PATH = r'C:\Users\ibkaa\nursinghomeguide-my\Nursing Home Guide Malaysia\token_sheets.json'
TODAY = '2026-05-03'

# ---------------------------------------------------------------------------
# Raw data from Apify run — keyed by slug
# Images: prefer lh3.../p/ URLs over gps-cs-s URLs, skip streetviewpixels
# ---------------------------------------------------------------------------
APIFY_DATA = {
    'pine-tree-home-care-centre-johor': {
        'phone': '+60 19-776 6666',
        'website': '',
        'rating': 3.0,
        'review_count': 1,
        'address': '277, Lorong Setia, Jalan Parit Mesjid, 82000 Pontian District, Johor, Malaysia',
        'latitude': 1.4941937,
        'longitude': 103.3947676,
        'google_maps_url': 'https://www.google.com/maps/search/?api=1&query=Pine+Tree+Home+Care+Centre+Pontian',
        'hero_image': 'https://lh3.googleusercontent.com/gps-cs-s/APNQkAF0FOz2Z_C8UZRJHGlTs3BeQq7BZ34VnGq6lDmEQDNiqHhupGtd2tNTWDuCJxK7h0l5EEhZ-q-fXfZ5MDHg7ADESOt7QkMH2N5P4T_2cTzDKNJPLl5C_GJbDNNBqN7LiOhlT-y=w427-h240-k-no',
        'photos': [],
        'imagesCount': 2,
    },
    'rebina-home-care-centre-sdn-bhd': {
        'phone': '',
        'website': '',
        'rating': 3.5,
        'review_count': 2,
        'address': '112, Jln Wijaya, Taman Abad, 80250 Johor Bahru, Johor Darul Ta\'zim, Malaysia',
        'latitude': 1.4854122,
        'longitude': 103.7569052,
        'google_maps_url': '',  # already has valid URL
        'hero_image': '',  # only streetview
        'photos': [],
        'imagesCount': 1,
    },
    'sunshine-nursing-home-care': {
        'phone': '+60 12-474 6615',
        'website': '',
        'rating': 3.0,
        'review_count': 2,
        'address': 'No 33, Jalan Teluki 2, Bukit Sentosa, 44300 Rawang, Selangor, Malaysia',
        'latitude': 3.4012764,
        'longitude': 101.5697774,
        'google_maps_url': '',
        'hero_image': '',  # only streetview
        'photos': [],
        'imagesCount': 1,
    },
    'aurora-home-care-centre': {
        'phone': '+60 16-690 6333',
        'website': 'https://www.facebook.com/Aurorahomecarecentre',
        'rating': 5.0,
        'review_count': 1,
        'address': '166e, Jalan Sireh, off, Jln Meru, Kawasan 17, 41050 Klang, Selangor, Malaysia',
        'latitude': 3.0509473,
        'longitude': 101.4525622,
        'google_maps_url': '',
        'hero_image': 'https://lh3.googleusercontent.com/gps-cs-s/APNQkAEfSoSeBEo-VCOlNVle_6KR_GCd8Rv5mhCzM-1_i5o8wtplELRA7Zg2i1DFQT3q4c3mTnl7g6fNPL4Cv8gC-Ee0S5zNQ0kOO0Nb1bC_LKf0P-71XhcBP08BcUWlJGy0UPZTvhh=w427-h240-k-no',
        'photos': ['https://lh3.googleusercontent.com/gps-cs-s/APNQkAEfSoSeBEo-VCOlNVle_6KR_GCd8Rv5mhCzM-1_i5o8wtplELRA7Zg2i1DFQT3q4c3mTnl7g6fNPL4Cv8gC-Ee0S5zNQ0kOO0Nb1bC_LKf0P-71XhcBP08BcUWlJGy0UPZTvhh=w427-h240-k-no'],
        'imagesCount': 2,
    },
    'ln-home-care-center': {
        'phone': '+60 19-888 8690',
        'website': '',
        'rating': 5.0,
        'review_count': 3,
        'address': 'Bunga ros Kawasan 6, Taman Teluk Pulai, 41100 Klang, Selangor, Malaysia',
        'latitude': 3.0419121,
        'longitude': 101.4398907,
        'google_maps_url': '',
        'hero_image': 'https://lh3.googleusercontent.com/gps-cs-s/APNQkAFfSwWBgIsumXlYxlJnQvcqggJ6H-7Hprg2cnaIFztLiVgdw2QyCUaqzHRlVxjB1wfpNJHFiLBiVVrqFlD2DKYHgJKJdCvwu1MHY0PbXHPJBUb7c00_5gDVPgEr5aNO7D9Oqkz=w427-h240-k-no',
        'photos': ['https://lh3.googleusercontent.com/gps-cs-s/APNQkAFfSwWBgIsumXlYxlJnQvcqggJ6H-7Hprg2cnaIFztLiVgdw2QyCUaqzHRlVxjB1wfpNJHFiLBiVVrqFlD2DKYHgJKJdCvwu1MHY0PbXHPJBUb7c00_5gDVPgEr5aNO7D9Oqkz=w427-h240-k-no'],
        'imagesCount': 2,
    },
    'my-peaceful-home-care-centre': {
        'phone': '+60 11-1281 2292',
        'website': 'https://mypeacefulhome.com.my/',
        'rating': 4.8,
        'review_count': 6,
        'address': '14, Jalan SS 19/3, Ss 19, 47500 Subang Jaya, Selangor, Malaysia',
        'latitude': 3.0717011,
        'longitude': 101.5773665,
        'google_maps_url': '',
        'hero_image': 'https://lh3.googleusercontent.com/gps-cs-s/APNQkAFVwlb8zpCXX2tCIBdVxnfbtVpU1-_COLpNg0bEG7RAdOlUj-JRkCMz2gq8kAVcEfO0e3NKy-u-SQ9R7LZQV40KLPaxELKDaGX0hV6hJ5Iiha1jU3nPjLBvJgU1GN_9y4t27s=w427-h240-k-no',
        'photos': ['https://lh3.googleusercontent.com/gps-cs-s/APNQkAFVwlb8zpCXX2tCIBdVxnfbtVpU1-_COLpNg0bEG7RAdOlUj-JRkCMz2gq8kAVcEfO0e3NKy-u-SQ9R7LZQV40KLPaxELKDaGX0hV6hJ5Iiha1jU3nPjLBvJgU1GN_9y4t27s=w427-h240-k-no'],
        'imagesCount': 3,
    },
    'his-grace-home-care-centre': {
        'phone': '+60 16-671 5732',
        'website': '',
        'rating': 5.0,
        'review_count': 2,
        'address': '4, Jalan Perusahaan 1, off Jalan Genting Kelang, Setapak, 53300 Kuala Lumpur, Malaysia',
        'latitude': 3.1966588,
        'longitude': 101.717454,
        'google_maps_url': '',
        'hero_image': 'https://lh3.googleusercontent.com/p/AF1QipMDShS_PmttaIHEdfUeiLoPg_hnPQATSAuLcgTn=w1920-h1080-k-no',
        'photos': [
            'https://lh3.googleusercontent.com/p/AF1QipMDShS_PmttaIHEdfUeiLoPg_hnPQATSAuLcgTn=w1920-h1080-k-no',
            'https://lh3.googleusercontent.com/p/AF1QipPuv4udHBlZWQ_w1TY2cPvFtY9-e3-vo93DgMOw=w1920-h1080-k-no',
        ],
        'imagesCount': 3,
    },
    'sayang-nursing-home-care': {
        'phone': '+60 3-5519 7501',
        'website': '',
        'rating': None,
        'review_count': 0,
        'address': 'Lot 2-01, 2nd Floor, Anggerik Mall, No. 5, Jalan 14/8, Seksyen 14, 40000 Shah Alam, Selangor, Malaysia',
        'latitude': 3.07131,
        'longitude': 101.519852,
        'google_maps_url': '',
        'hero_image': '',
        'photos': [],
        'imagesCount': 1,
    },
    'sree-sai-elder-home-care-mental-health-old-age-residential-home': {
        'phone': '+60 12-297 0597',
        'website': '',
        'rating': 5.0,
        'review_count': 6,
        'address': 'No. 204 B, Off, Jln Ampang, Kuala Ampang, 55000 Kuala Lumpur, Malaysia',
        'latitude': 3.1610367,
        'longitude': 101.7251654,
        'google_maps_url': '',
        'hero_image': 'https://lh3.googleusercontent.com/gps-cs-s/APNQkAGTAhjEVaUXYCQNceUlQD7n5fcVIEHm94Z7BbnDS1-1rWUTB9q1JZXCDO7oy4eaJ07y0LBH3VrFz-_6V5jlW0lM1QqgXAzXE4fVVq3JuOK9K3Lq0xXWE7-u7bCqkCpRlAHLRE=w427-h240-k-no',
        'photos': [
            'https://lh3.googleusercontent.com/gps-cs-s/APNQkAGTAhjEVaUXYCQNceUlQD7n5fcVIEHm94Z7BbnDS1-1rWUTB9q1JZXCDO7oy4eaJ07y0LBH3VrFz-_6V5jlW0lM1QqgXAzXE4fVVq3JuOK9K3Lq0xXWE7-u7bCqkCpRlAHLRE=w427-h240-k-no',
            'https://lh3.googleusercontent.com/gps-cs-s/APNQkAFigFd5l_slyhadiLzIOa_HNLpkxdna7jOQTQxa5hBY8hzvp6majkFmjVMbP0pHO0HqGLVg9UXmIwqQ_7v6eSQXnzVmPRDthJt3I0LJcz0p5X6TQrY-z5cWrL2sHuRhlpJbQo=w427-h240-k-no',
        ],
        'imagesCount': 3,
    },
    'bandar-damai-home-care': {
        'phone': '+60 3-9101 7930',
        'website': 'http://bandardamaihomecare.wixsite.com/bandardamaihomecare',
        'rating': 4.5,
        'review_count': 2,
        'address': 'No. 24, Jalan Damai Perdana 2/6f, Bandar Damai Perdana, 56000 Kuala Lumpur, Malaysia',
        'latitude': 3.0447747,
        'longitude': 101.7386822,
        'google_maps_url': '',
        'hero_image': 'https://lh3.googleusercontent.com/gps-cs-s/APNQkAFQFK5K0dsBbSQHkmp_RNWdqj-C1m3TRBHPSqOBRFaLVkNedNmD_KMDfAdTI_FN5TL_G3mAkyxDWIk8HI_qE0uq1cbxMp8x7mzU1fxcTG5UiF7wz3Gse_F2HOobkI7n5MvKyU=w427-h240-k-no',
        'photos': [
            'https://lh3.googleusercontent.com/gps-cs-s/APNQkAFQFK5K0dsBbSQHkmp_RNWdqj-C1m3TRBHPSqOBRFaLVkNedNmD_KMDfAdTI_FN5TL_G3mAkyxDWIk8HI_qE0uq1cbxMp8x7mzU1fxcTG5UiF7wz3Gse_F2HOobkI7n5MvKyU=w427-h240-k-no',
            'https://lh3.googleusercontent.com/gps-cs-s/APNQkAEPMmvfHkyoI5oa67U3WobF1uZO256gdeBXMgkqDtc0a54ZF1HuxmIQpVWDhDRrPm7UuYt-EJ0jJwWmQxUAiGPmqjp9fcFDVlDiVNAOZPF6I58CW6wBs4hPaH0_eE0BVxJCQf=w427-h240-k-no',
        ],
        'imagesCount': 3,
    },
    'his-grace-home-care-centretaman-pramlee': {
        'phone': '+60 11-1162 5831',
        'website': '',
        'rating': 4.5,
        'review_count': 2,
        'address': '10, Jalan Cempaka, Taman P Ramlee, 53000 Kuala Lumpur, Malaysia',
        'latitude': 3.1930011,
        'longitude': 101.7070555,
        'google_maps_url': '',
        'hero_image': 'https://lh3.googleusercontent.com/p/AF1QipO6BkJD15ERVU10Cks3ZMvKWO-FeVt5nhR8nuF_=w1920-h1080-k-no',
        'photos': [
            'https://lh3.googleusercontent.com/p/AF1QipO6BkJD15ERVU10Cks3ZMvKWO-FeVt5nhR8nuF_=w1920-h1080-k-no',
            'https://lh3.googleusercontent.com/p/AF1QipPq9H_o4Jpm4qn_Xbx3kvKZtAWR-xj9witlQG5a=w1920-h1080-k-no',
            'https://lh3.googleusercontent.com/p/AF1QipMjblfj--aI-WCNbQ8KZ9Cnuoz2Is-p6X0tasq_=w1920-h1080-k-no',
            'https://lh3.googleusercontent.com/p/AF1QipPNnjnyZUGbnEbfmD9rt1zdYxWUYb6MQhm5t-Cw=w1920-h1080-k-no',
            'https://lh3.googleusercontent.com/p/AF1QipMYR_LG2yeNW7t42pMlvCIUzeO-P3D7XMOvA2hZOdAjD3-EGQta=w427-h240-k-no',
        ],
        'imagesCount': 18,
    },
    'home-sweet-home-care-centre-jalan-gasing': {
        'phone': '+60 16-603 6821',
        'website': 'https://web.facebook.com/homesweethomecarecentre',
        'rating': 5.0,
        'review_count': 3,
        'address': '43, Jalan Gasing, Bukit Gasing, 46000 Petaling Jaya, Selangor, Malaysia',
        'latitude': 3.0977233,
        'longitude': 101.6517129,
        'google_maps_url': '',
        'hero_image': 'https://lh3.googleusercontent.com/p/AF1QipOmq_17rP3djG46HSo8ZFlrUlkFEQ68Dch7if3U=w1920-h1080-k-no',
        'photos': [
            'https://lh3.googleusercontent.com/p/AF1QipOmq_17rP3djG46HSo8ZFlrUlkFEQ68Dch7if3U=w1920-h1080-k-no',
            'https://lh3.googleusercontent.com/p/AF1QipO5c_IbROPap5u8puF1AA41Xpc9h_PdyG6gpNnY=w1920-h1080-k-no',
            'https://lh3.googleusercontent.com/gps-cs-s/APNQkAGVHfyWV4h4ayI_1q0U3jyloed3plS_CMiUgw5hZsdwF3KGF12ZvVTfS_0FRuYr1BjQ8yB1AYfSh9-IidHdHN_iCdXX_uLi5aK3haMVbPNMKANMkISSjPiVYMHB4aqkz7Xvhu=w427-h240-k-no',
        ],
        'imagesCount': 4,
    },
    'city-home-care-centre': {
        'phone': '+60 16-612 3368',
        'website': 'https://dannycarecentre.wixsite.com/mysite',
        'rating': 1.7,
        'review_count': 6,
        'address': '20, Lorong Kadok, Taman Chi Liung, 41200 Klang, Selangor, Malaysia',
        'latitude': 3.0218139,
        'longitude': 101.4358331,
        'google_maps_url': '',
        'hero_image': 'https://lh3.googleusercontent.com/p/AF1QipNm-pDB7zhVf9kBkuVomXBsx0NlvZsu2QkTaCxO=w1920-h1080-k-no',
        'photos': [
            'https://lh3.googleusercontent.com/p/AF1QipNm-pDB7zhVf9kBkuVomXBsx0NlvZsu2QkTaCxO=w1920-h1080-k-no',
            'https://lh3.googleusercontent.com/gps-cs-s/APNQkAF8V1A7kceBaWskYYKdodrhntTFzrSbXl8JLrHXH676Uso7LBIWo3RRe1fxPjUdlIAtaMIqMVZjYmrNrEtnU3I5rYLSzQPgp7xBQfqHzsTUiXqFQAVhaMPZ_wLQ-mwNGYU_e6U=w427-h240-k-no',
            'https://lh3.googleusercontent.com/gps-cs-s/APNQkAGbjh8jO_Ul8G4NsPZ9JMYI5EIz49KTIemNGc4D0S6c7J3KWW84JHe6LqUVhsF0GsKNZLl2pHHuniGj5V3gUlX9Vz6lG0DWYB_iBNO58o50Y6j8D_pRaKF8gI9VaRG-0Zyxqn=w427-h240-k-no',
        ],
        'imagesCount': 10,
    },
    'good-family-home-care': {
        'phone': '',
        'website': '',
        'rating': None,
        'review_count': 0,
        'address': '799, Lorong Permai 14, Kampung Tasek Permai, 68000 Ampang, Selangor, Malaysia',
        'latitude': 3.1299679,
        'longitude': 101.7824552,
        'google_maps_url': '',
        'hero_image': 'https://lh3.googleusercontent.com/gps-cs-s/APNQkAG7iKx-DVQ8LCaWaIhHpWrV2YDFmLTHia8oitCrwqXJ5jcTZyRsuKBNI5KV3-y3ZzFPxV_Taqjk8OiQ2P2WlkWfMEK-Iy5E3h7TuYZqSnlWpj59-y4EWoVFGEZPBfF-nYcCE4=w427-h240-k-no',
        'photos': [
            'https://lh3.googleusercontent.com/gps-cs-s/APNQkAG7iKx-DVQ8LCaWaIhHpWrV2YDFmLTHia8oitCrwqXJ5jcTZyRsuKBNI5KV3-y3ZzFPxV_Taqjk8OiQ2P2WlkWfMEK-Iy5E3h7TuYZqSnlWpj59-y4EWoVFGEZPBfF-nYcCE4=w427-h240-k-no',
            'https://lh3.googleusercontent.com/gps-cs-s/APNQkAH01ASS5L78xTQS6OqtDg1H-2i2-REQ7_Dlo5EHnCVoIzIxQ7OhiGqgDqME6DxkRLSfq1DlTBuOb7wgFk30GcHe0cZIb3o-WF1tBJkDdNNJE1pM2qhb7nQ6OhI73-dE4KkjKs=w427-h240-k-no',
            'https://lh3.googleusercontent.com/gps-cs-s/APNQkAG0Ju5L0gfQu92xbK83OwtOV-ZZwfRwXJK5-pj6yQG_2XRhcquXxf5JXuopbBbFxjqnCbBpGFimRrLB--O9QM4EKGRbKlG50SnBZBX7EvxFGmN_m2g5G1RWuEHNrCmM6JWDZo=w427-h240-k-no',
            'https://lh3.googleusercontent.com/gps-cs-s/APNQkAGGRUhZfwsBtVrmxnkIfpQqHs2WKYkjHSRn6bc6fB74mLfibY6MOi8t8Uc9HBfzevWfOZ1ztRBCf32K3P3gT0bC1_JzHGST7F1W_HBkSqvZk7J8CJD3vJqosPbTMDPSnHmFbs=w427-h240-k-no',
        ],
        'imagesCount': 9,
    },
    'prowell-elderly-home-care-centre-hq': {
        'phone': '+60 12-530 1478',
        'website': 'http://www.pehcc.com.my/',
        'rating': 4.1,
        'review_count': 7,
        'address': '17-1, Jalan Dato Haji Harun, Taman Taynton View, 56000 Cheras, Kuala Lumpur, Malaysia',
        'latitude': 3.087806,
        'longitude': 101.7390751,
        'google_maps_url': '',
        'hero_image': 'https://lh3.googleusercontent.com/p/AF1QipMwCbUsKFUbBlZnh218m8ZCb5ZWwZTzdHpGYc0E=w1920-h1080-k-no',
        'photos': [
            'https://lh3.googleusercontent.com/p/AF1QipMwCbUsKFUbBlZnh218m8ZCb5ZWwZTzdHpGYc0E=w1920-h1080-k-no',
            'https://lh3.googleusercontent.com/p/AF1QipOIyfOLprZ3R32t1N9vZ9QmQPE2_a_QMhGlRP2i=w1920-h1080-k-no',
            'https://lh3.googleusercontent.com/p/AF1QipNaWs38s3sbIzeyY5t2vyJRibdjpcsXQslWaWMn=w1920-h1080-k-no',
            'https://lh3.googleusercontent.com/p/AF1QipPokCskEEWPlVFzS0AgSdCaphEHPieo9_7wwFg8=w1920-h1080-k-no',
            'https://lh3.googleusercontent.com/p/AF1QipPfdsR89ekmA9bdA6ZT3nzTt_8irfdN2FGp1Eat=w1920-h1080-k-no',
        ],
        'imagesCount': 19,
    },
    'my-joyful-home-care-centre': {
        'phone': '+60 19-329 3855',
        'website': 'https://myjoyfulhome.com.my/',
        'rating': 5.0,
        'review_count': 8,
        'address': '12, Jalan SS 19/3, Ss 19, 47500 Subang Jaya, Selangor, Malaysia',
        'latitude': 3.0718149,
        'longitude': 101.5776148,
        'google_maps_url': '',
        'hero_image': 'https://lh3.googleusercontent.com/p/AF1QipMXW9QrbneWIF6NhfX1wzy-wGNxIO10YW3hr1nV=w1920-h1080-k-no',
        'photos': [
            'https://lh3.googleusercontent.com/p/AF1QipMXW9QrbneWIF6NhfX1wzy-wGNxIO10YW3hr1nV=w1920-h1080-k-no',
            'https://lh3.googleusercontent.com/p/AF1QipMIMUgA7qSa1a0nAKFDf8EKay_TifvizaMkSqvt=w1920-h1080-k-no',
            'https://lh3.googleusercontent.com/gps-cs-s/APNQkAHRPBRBfjO_ivQmamEmV1eoYbZFivEV-DAbR4zIE2OIb-eKjUDcOoLSXAFkjnFw7l5MJH14fJQKVmVyg-i1s_lHqAkA_nQAG8WE4PfmmrY-CGxE8qPJuqFsrZK5mHDGU0_kAU=w427-h240-k-no',
            'https://lh3.googleusercontent.com/gps-cs-s/APNQkAHLr34TpHO3maIPkQXuLIrknKCg5JF6JpDkCqmtPF3bNPnAIbFYcJzlQg_1cVsMp6E0Y4k7RvDQCqF-0xlBfpMT5YN0j7X3mQPZy8fSjjJFiJO6y5H4FZc6t1M5gRQknBN5Go=w427-h240-k-no',
            'https://lh3.googleusercontent.com/gps-cs-s/APNQkAEypEU-xovwGYrJfvf5Nh9juREIq_SpgxJU6TvlhrZUqFFQZebKA2fPPXzHYi5yY-LMOuHv1eK6H3I-Ksn10n1U4RO7sJfq4q5YYqHF1oQ3a9ZJuHfyWrXNx_v8-rjAtHhVnY=w427-h240-k-no',
        ],
        'imagesCount': 14,
    },
    'my-precious-home-care-elder-care': {
        'phone': '+60 16-311 9469',
        'website': 'http://www.myprecioushomecare.com/',
        'rating': 4.7,
        'review_count': 122,
        'address': '27 Jalan USJ 1/3B, Taman Subang Mewah, Grandville, 47600 Subang Jaya, Selangor, Malaysia',
        'latitude': 3.0537416,
        'longitude': 101.6066365,
        'google_maps_url': '',
        'hero_image': 'https://lh3.googleusercontent.com/p/AF1QipNJW4PdFOxzTVvmOw--3pT3LIrf_tpIitwuIOyh=w1920-h1080-k-no',
        'photos': [
            'https://lh3.googleusercontent.com/p/AF1QipNJW4PdFOxzTVvmOw--3pT3LIrf_tpIitwuIOyh=w1920-h1080-k-no',
            'https://lh3.googleusercontent.com/p/AF1QipNqmjw17rMiqaDuM9f9SQmk71eC-SHE-V4l9JND=w1920-h1080-k-no',
            'https://lh3.googleusercontent.com/p/AF1QipN8w8_vtgmRWlGEetlsBQsqggb9TSos_kzm86P8=w1920-h1080-k-no',
            'https://lh3.googleusercontent.com/gps-cs-s/APNQkAGVp6i_psRj6eg-qDPbU7J2Y8H9TC5Bw9QkIdAcvPGEB1CN-fkqlx9oDvLDa3eLA3aWXM_aKINyZbPjAk3IQ3lgwRvzO2ulucakesKzOe_BgnJjpDETlMwtzyyIhSQPJMUOk0-k=w427-h240-k-no',
            'https://lh3.googleusercontent.com/gps-cs-s/APNQkAEITFQ-iRq1zznLDW5OoDIltExyvP-CHnpnEVMAlVK2GQIYLniyx_Nmt2JJtxHFNDPYWmcVx7yqF81S2GEqOXcFJ5hY56FULXqlKvuX-HiFWVGnXpFv-vNgHiblj3uqzj3HWwQ=w427-h240-k-no',
        ],
        'imagesCount': 94,
    },
    'rs-global-home-care-only-for-muslim': {
        'phone': '+60 11-3586 0025',
        'website': '',
        'rating': 4.7,
        'review_count': 18,
        'address': '1 C, Jalan 2, Kampung Cheras Baru, 56100 Kuala Lumpur, Malaysia',
        'latitude': 3.1101109,
        'longitude': 101.7461885,
        'google_maps_url': '',
        'hero_image': 'https://lh3.googleusercontent.com/p/AF1QipOGhmhCwcA__WUDPaosF0rTeJKk2sudK5HlOF-5=w1920-h1080-k-no',
        'photos': [
            'https://lh3.googleusercontent.com/p/AF1QipOGhmhCwcA__WUDPaosF0rTeJKk2sudK5HlOF-5=w1920-h1080-k-no',
            'https://lh3.googleusercontent.com/p/AF1QipPOR90vK5AXs3gD7SQ-WUw269tWuSxlVQUqXZem=w1920-h1080-k-no',
            'https://lh3.googleusercontent.com/p/AF1QipOnFAeMFxkcRfjvDGVxoodh-X1iuBsf0zgH2gnj=w1920-h1080-k-no',
            'https://lh3.googleusercontent.com/p/AF1QipMJlkmx6SIUE9PclY9JhFbZNYgALonAidb5vfl0=w1920-h1080-k-no',
            'https://lh3.googleusercontent.com/gps-cs-s/APNQkAESmBvkVd3kXGvw9TxfuZlXkGMg5I9IkrPkqX03F1q3ld8SWao0h_ZhZ3bQqHJxGFlQ9Km-kSj9lKBHWUg5g4w2MJY-_Wqs8l1-3V3JCu2PzmKQbJkb1mMn0Xq3gIQVY5M_NI=w427-h240-k-no',
        ],
        'imagesCount': 224,
    },
    'mintygreen-care-suites-home-care-nursing-cheras-kl': {
        'phone': '+60 11-5587 9788',
        'website': 'https://www.mintygreen-wellness.com/',
        'rating': 4.8,
        'review_count': 22,
        'address': '100, Jln Cheras, Phoenix Business Park, 56000 Kuala Lumpur, Malaysia',
        'latitude': 3.0788963,
        'longitude': 101.7443207,
        'google_maps_url': '',
        'hero_image': 'https://lh3.googleusercontent.com/p/AF1QipP54NlVHs6qnnD2g-FPq2NBxZkz_Bjl1DyL1-DY=w1920-h1080-k-no',
        'photos': [
            'https://lh3.googleusercontent.com/p/AF1QipP54NlVHs6qnnD2g-FPq2NBxZkz_Bjl1DyL1-DY=w1920-h1080-k-no',
            'https://lh3.googleusercontent.com/p/AF1QipPPgkH47tNZwJufvI8OLT_8p_VfyBbKqP7ltriL=w1920-h1080-k-no',
            'https://lh3.googleusercontent.com/p/AF1QipMlDb-U9zQ2ya4GAxMl3QJ1jQ3vnw0N4n5vWkyy=w1920-h1080-k-no',
            'https://lh3.googleusercontent.com/p/AF1QipN2nOXZ9q0PQFZMtr6x0T7WXmLVYTOivvY08TMe=w1920-h1080-k-no',
            'https://lh3.googleusercontent.com/gps-cs-s/APNQkAEQGujKVkIkTE8vsOiRaoOnG3dV3oyJVYwQ4ebEnMmJiHzXSpsvJcJXvXnr9OLIhFAx-JlBFtYT29GIQT1GRXanJmMG06sqb2WE5hjb-VkbqgVCE58K5XpQSuNDvgFbqI4Jnzk=w427-h240-k-no',
        ],
        'imagesCount': 26,
    },
    'comfort-home-care-centre': {
        'phone': '+60 12-696 9403',
        'website': '',
        'rating': 5.0,
        'review_count': 5,
        'address': '56 Jalan Kampung Tengah 1/2, Taman Kampung Tengah, 84000 Muar, Johor, Malaysia',
        'latitude': 2.065159,
        'longitude': 102.6047471,
        'google_maps_url': '',
        'hero_image': 'https://lh3.googleusercontent.com/gps-cs-s/APNQkAHGowj4trg7NBTb9qh_2ykHP1J0Lxw7i9YDPgEnY4Col3oL7AIRLd5GnmH-q2B8W0kW0cEgdLmyh3AH4FZAJ5eGNDcMUFmJHwG1ULXmhzK5dMYfBSdB_axZNdF5aMzwcEjrbo=w427-h240-k-no',
        'photos': [
            'https://lh3.googleusercontent.com/gps-cs-s/APNQkAHGowj4trg7NBTb9qh_2ykHP1J0Lxw7i9YDPgEnY4Col3oL7AIRLd5GnmH-q2B8W0kW0cEgdLmyh3AH4FZAJ5eGNDcMUFmJHwG1ULXmhzK5dMYfBSdB_axZNdF5aMzwcEjrbo=w427-h240-k-no',
            'https://lh3.googleusercontent.com/gps-cs-s/APNQkAHk7CwZi3w-yly4mKcx7NiXTf3SYvssW5-s7-TXtt6Ugn6ebZYmSBt33Gtu6szn9FaYT-SLaBzqgPqYB2-SFWjeMjEq1p-3NqdYzAeV97K2lKXwm5M3tN7gNJdZY3YCTD8D7w=w427-h240-k-no',
            'https://lh3.googleusercontent.com/gps-cs-s/APNQkAGE79XXbl9DSOZcjQh7gUfBUGxkzjnkmrWlxwl7pdWPc0kkMf2rZQKV7GJKJ5p6EcFLlnhCEUbH7j_eLFxTdKAh-HMJjHlJi79YaVBM-8LJo7bvqOw5wKfPRRZGVCN2OPIVHY=w427-h240-k-no',
            'https://lh3.googleusercontent.com/gps-cs-s/APNQkAFEU9OcJil8viXA7uu3FxlOMBgASpGNR_3USQZw-aCYOfmolpFprxfN0HH7MFpMiPIWNbVYAf4JjZ5mhcl6bTDniMfFCKgpQvdIDGRt74Fq0Gd1Z-R4VR3tEBmipHkwNAIR56U=w427-h240-k-no',
            'https://lh3.googleusercontent.com/gps-cs-s/APNQkAHTyXFL-ZIA0VkoKURc080xN3sLDZQK8-zzFBuow-fvruzvM1SlhD2SHnFrHxO_sQBg2p19zr6bWLEK2RI6sj_X0R8UoxSzZVAHVU2tkm_EKOXTqKFQGBj0hNBNBVzFT3a9ZHo=w427-h240-k-no',
        ],
        'imagesCount': 11,
    },
    'my-precious-home-care-retirement-home': {
        'phone': '+60 11-7489 9115',
        'website': 'https://myprecioushomecare.com/',
        'rating': 5.0,
        'review_count': 11,
        'address': 'No. 38, Jalan SS1/39, Kampung Tunku, 47300 Petaling Jaya, Selangor, Malaysia',
        'latitude': 3.1031753,
        'longitude': 101.6218464,
        'google_maps_url': '',
        'hero_image': 'https://lh3.googleusercontent.com/p/AF1QipMdizBVOqNNVqfo6uAQW0CwaDY3Ezt9QLDJsEAE=w1920-h1080-k-no',
        'photos': [
            'https://lh3.googleusercontent.com/p/AF1QipMdizBVOqNNVqfo6uAQW0CwaDY3Ezt9QLDJsEAE=w1920-h1080-k-no',
            'https://lh3.googleusercontent.com/p/AF1QipMc3TSxntzHQ_jWOUSN5FxeElMK1G-VAQjZlt-3=w1920-h1080-k-no',
            'https://lh3.googleusercontent.com/p/AF1QipP-e-JNVJd4keHxn3EuIL-kKs8NMHkZMPesEmn_=w1920-h1080-k-no',
            'https://lh3.googleusercontent.com/p/AF1QipMa_2xQLSFkkdFQeVqMpB3VJp0Ndzn0MZEuuuoR=w1920-h1080-k-no',
            'https://lh3.googleusercontent.com/p/AF1QipMijSPrhlGxHrTuB2CLDcbzK3T06MjZoZqww-61=w1920-h1080-k-no',
        ],
        'imagesCount': 39,
    },
}


# ---------------------------------------------------------------------------
# Google Sheets helpers
# ---------------------------------------------------------------------------

def col_letter(idx):
    """Convert 0-based column index to A1 letter."""
    s = ''
    idx += 1
    while idx:
        idx, rem = divmod(idx - 1, 26)
        s = chr(65 + rem) + s
    return s


def load_sheet():
    creds = Credentials.from_authorized_user_file(TOKEN_PATH, scopes=['https://www.googleapis.com/auth/spreadsheets'])
    svc = build('sheets', 'v4', credentials=creds)
    result = svc.spreadsheets().values().get(
        spreadsheetId=SHEET_ID,
        range=f'{SHEET_TAB}!1:1'
    ).execute()
    headers = result['values'][0]

    result2 = svc.spreadsheets().values().get(
        spreadsheetId=SHEET_ID,
        range=f'{SHEET_TAB}!B:B'
    ).execute()
    slugs = [row[0] if row else '' for row in result2.get('values', [])]
    return svc, headers, slugs


def find_row(slugs, slug):
    for i, s in enumerate(slugs):
        if s == slug:
            return i + 1  # 1-based sheet row
    return None


def push_updates(svc, headers, slugs):
    updates = []
    skipped = []

    for slug, data in APIFY_DATA.items():
        row = find_row(slugs, slug)
        if not row:
            print(f'SKIP (not found in sheet): {slug}')
            skipped.append(slug)
            continue

        def cell(col_name, value):
            if col_name not in headers:
                print(f'  WARNING: column "{col_name}" not in headers')
                return
            col_idx = headers.index(col_name)
            col_let = col_letter(col_idx)
            updates.append({
                'range': f'{SHEET_TAB}!{col_let}{row}',
                'values': [[value]]
            })

        # Phone — only update if non-empty in Apify data and we have a value
        if data['phone']:
            cell('phone', data['phone'])

        # Website — only update if real (not Facebook-only already) and found
        if data['website'] and 'facebook' not in data['website'].lower():
            cell('website', data['website'])

        # Rating + review count
        if data['rating'] is not None:
            cell('rating', data['rating'])
        if data['review_count'] > 0:
            cell('review_count', data['review_count'])

        # Coordinates
        if data['latitude']:
            cell('latitude', data['latitude'])
        if data['longitude']:
            cell('longitude', data['longitude'])

        # Google Maps URL fix (only for the two corrupted ones)
        if data['google_maps_url']:
            cell('google_maps_url', data['google_maps_url'])

        # Photos
        if data['hero_image']:
            cell('hero_image', data['hero_image'])

        photos = data['photos']
        if photos:
            cell('photos', '|'.join(photos[:5]))
            cell('photo_count', min(data['imagesCount'], 5))
        elif data['imagesCount'] > 0:
            # Even if no photos collected, update count
            cell('photo_count', data['imagesCount'])

        # last_updated
        cell('last_updated', TODAY)

        print(f'  Queued {len([u for u in updates if f"!{col_letter(0)}" not in u.get("range","")])} updates for {slug} (row {row})')

    if not updates:
        print('No updates to push.')
        return

    print(f'\nPushing {len(updates)} cell updates...')
    body = {'valueInputOption': 'USER_ENTERED', 'data': updates}
    resp = svc.spreadsheets().values().batchUpdate(
        spreadsheetId=SHEET_ID, body=body
    ).execute()
    print(f'Updated {resp.get("totalUpdatedCells",0)} cells across {resp.get("totalUpdatedRows",0)} rows.')
    if skipped:
        print(f'Skipped slugs: {skipped}')


if __name__ == '__main__':
    print('Loading sheet...')
    svc, headers, slugs = load_sheet()
    print(f'Sheet loaded. {len(slugs)} rows, {len(headers)} columns.')
    print(f'Processing {len(APIFY_DATA)} slugs...')
    push_updates(svc, headers, slugs)
    print('Done.')
