from flask import Flask, render_template, request, jsonify
import qrcode
import io
import base64
import random
import smtplib
import threading
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)

REVOLUT_IBAN = "LT803250069633761109"
ADMIN_EMAIL = "ruzar7789@gmail.com"
SENDER_PASSWORD = "ipomueicxxgxbumn"

SERVICES = {
    "tarot_basic": {
        "title": "Základní výklad Tarotu (3 karty)",
        "price": 25.00,
        "currency": "EUR",
        "description": "Rozbor minulosti, přítomnosti a směřování v blízké budoucnosti."
    },
    "tarot_full": {
        "title": "Kompletní roční horoskop a Tarot",
        "price": 75.00,
        "currency": "EUR",
        "description": "Detailní vhled do 12 měsíců: financí, vztahů, zdraví a kariéry."
    },
    "ritual_love": {
        "title": "Mistrovský rituál harmonizace vztahu",
        "price": 150.00,
        "currency": "EUR",
        "description": "Hluboká energetická očista a posílení poutek s partnerem."
    },
    "ritual_protection": {
        "title": "Velký rituál osobní a majetkové ochrany",
        "price": 250.00,
        "currency": "EUR",
        "description": "Odstranění negativních bloků a vytvoření ochranného štítu."
    },
    "consultation_vip": {
        "title": "Osobní VIP konzultace (60 minut)",
        "price": 120.00,
        "currency": "EUR",
        "description": "Individuální setkání nebo online hovor s rozborem situace."
    }
}

TAROT_CARDS = [
    {"name": "I. Mág", "meaning": "Absolutní potenciál, manifestace záměrů, vůle a tvořivá síla."},
    {"name": "II. Velekněžka", "meaning": "Intuice, tajemství, vnitřní hlas a hluboké podvědomé vědění."},
    {"name": "III. Císařovna", "meaning": "Hojnost, plodnost, přírodní růst a emocionální naplnění."},
    {"name": "IV. Císař", "meaning": "Pevná struktura, autorita, stabilita a kontrola nad situací."},
    {"name": "V. Velekněz", "meaning": "Tradiční moudrost, duchovní vedení, učení a morální hodnoty."},
    {"name": "VI. Milenci", "meaning": "Láska, osudové rozhodnutí, harmonie vztahů a soulad."},
    {"name": "VII. Vůz", "meaning": "Triumf, odhodlání, překonání překážek a pohyb vpřed."},
    {"name": "VIII. Síla", "meaning": "Vnitřní síla, trpělivost, soucit a kontrola emocí."},
    {"name": "IX. Poustevník", "meaning": "Vnitřní moudrost, nalezení vlastní cesty skrze sebereflexi."},
    {"name": "X. Kolo Štěstěny", "meaning": "Osudový zvrat, cyklická změna, nová životní příležitost."},
    {"name": "XI. Spravedlnost", "meaning": "Pravda, rovnováha, příčina a následek, fér jednání."},
    {"name": "XII. Viselec", "meaning": "Nový úhel pohledu, oběť pro vyšší cíl, pauza v jednání."},
    {"name": "XIII. Smrt", "meaning": "Konec starého cyklu, transformace, hluboká obroda."},
    {"name": "XIV. Mírnost", "meaning": "Vyváženost, trpělivost, uzdravení a harmonické spojení."},
    {"name": "XV. Ďábel", "meaning": "Pouta, pokušení, závislost nebo nevědomá omezení."},
    {"name": "XVI. Věž", "meaning": "Náhlý zvrat, odhalení iluzí, osvobození od starých struktur."},
    {"name": "XVII. Hvězda", "meaning": "Naděje, inspirace, duchovní vedení a vnitřní klid."},
    {"name": "XVIII. Měsíc", "meaning": "Iluze, snění, hluboké podvědomé strachy a tajemství."},
    {"name": "XIX. Slunce", "meaning": "Jasnost, životní energie, triumf, radost a uzdravení."},
    {"name": "XX. Poslední soud", "meaning": "Procitnutí, znovuzrození, vyjasnění a vyšší volání."},
    {"name": "XXI. Svět", "meaning": "Dokončení cyklu, integrace, dosažení cíle a harmonie."}
]

def send_async_email(subject, body):
    try:
        msg = MIMEMultipart()
        msg['From'] = ADMIN_EMAIL
        msg['To'] = ADMIN_EMAIL
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain', 'utf-8'))

        # Použití SSL spojení na portu 465 (spolehlivější pro Render)
        with smtplib.SMTP_SSL('smtp.gmail.com', 465, timeout=15) as server:
            server.login(ADMIN_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)
            
        print("✅ E-mail byl úspěšně odeslán na Gmail.")
    except Exception as e:
        print(f"❌ Chyba při odesílání e-mailu: {e}")

@app.route('/')
def home():
    return render_template('index.html', services=SERVICES)

@app.route('/api/draw-card', methods=['GET'])
def draw_card():
    mode = request.args.get('mode', 'single')
    if mode == 'three':
        cards = random.sample(TAROT_CARDS, 3)
        return jsonify({
            "past": cards[0],
            "present": cards[1],
            "future": cards[2]
        })
    else:
        card = random.choice(TAROT_CARDS)
        return jsonify(card)

@app.route('/api/generate-qr', methods=['POST'])
def generate_qr():
    data = request.json or {}
    service_id = data.get('service_id', 'tarot_basic')
    service = SERVICES.get(service_id, SERVICES['tarot_basic'])
    
    amount = service['price']
    message = service['title'][:35]
    vs = str(random.randint(100000, 999999))

    sepa_string = (
        f"BCD\n002\n1\nSCT\n\n"
        f"Mystická Svatyně\n"
        f"{REVOLUT_IBAN}\n"
        f"EUR{amount:.2f}\n\n\n"
        f"{message} Ref:{vs}"
    )

    qr = qrcode.QRCode(version=1, box_size=8, border=2)
    qr.add_data(sepa_string)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#d4af37", back_color="#0a0512")

    buf = io.BytesIO()
    img.save(buf, format='PNG')
    qr_b64 = base64.b64encode(buf.getvalue()).decode('utf-8')

    return jsonify({
        "qr_image": f"data:image/png;base64,{qr_b64}",
        "title": service['title'],
        "price": f"{amount:.2f} EUR",
        "iban": REVOLUT_IBAN,
        "vs": vs
    })

@app.route('/api/reserve', methods=['POST'])
def reserve():
    data = request.json or {}
    email = data.get('email', '')
    service_key = data.get('service', 'tarot_basic')
    note = data.get('note', '')
    
    service_title = SERVICES.get(service_key, {}).get('title', 'Neznámá služba')
    reference_number = f"RES-{random.randint(1000, 9999)}"

    subject = f"Nová rezervace: {reference_number} - Mystická Svatyně"
    body = f"""
Nová rezervace ze stránek Mystická Svatyně!

Číslo rezervace: {reference_number}
E-mail klienta: {email}
Vybraná služba: {service_title}
Poznámka / Dotaz: {note}
    """

    # Odeslání na pozadí
    threading.Thread(target=send_async_email, args=(subject, body)).start()

    return jsonify({
        "status": "success",
        "message": f"Rezervace č. {reference_number} byla úspěšně odeslána! Potvrzení bude zpracováno."
    })

@app.route('/api/chat', methods=['POST'])
def chat():
    user_msg = request.json.get('message', '').lower()
    if "rituál" in user_msg or "očista" in user_msg:
        reply = "Vysoce účinné rituály probíhají v návaznosti na fáze Měsíce. Vyplňte rezervaci pod ceníkem."
    elif "vztah" in user_msg or "láska" in user_msg:
        reply = "Partnerské vazby zkoumáme přes karmický rozbor. Doporučuji Rituál harmonizace."
    elif "cena" in user_msg or "platba" in user_msg:
        reply = "Platby probíhají bezpečně přes SEPA QR kód přímo v EUR na náš účet."
    else:
        reply = "Vítám vás v Mystické Svatyni. Jakému tématu se dnes budeme věnovat?"
    return jsonify({"reply": reply})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
