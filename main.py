from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters,
    CallbackQueryHandler,
)
import re
import asyncio
from datetime import datetime
import os
import base64
from bakong_khqr import KHQR
from io import BytesIO
from PIL import Image
import io

# Conversation states
(
    LANGUAGE,
    CV_TYPE,
    NAME,
    ADDRESS,
    PHONE,
    POSITION,
    NATIONALITY,
    SEX,
    MARITAL,
    HEIGHT,
    WEIGHT,
    DOB,
    POB,
    PHOTO,
    ID_CARD_FRONT,
    ID_CARD_BACK,
    GAME,
    EXPERIENCE,
    EDUCATION,
    LANGUAGES,
    PAYMENT_CURRENCY,
    PAYMENT_VERIFICATION,
) = range(22)

# Admin Telegram ID
ADMIN_ID = 1081724526

# Bakong Configuration - REPLACE WITH YOUR ACTUAL CREDENTIALS
BAKONG_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJkYXRhIjp7ImlkIjoiMzYyZTU0Y2RmNDk2NDUzNSJ9LCJpYXQiOjE3NzAyNzc1MDgsImV4cCI6MTc3ODA1MzUwOH0.aOBTstZ-w_f7LqyUUd-KQ3jjxBlSywOnEFx4-CMVHVQ"
BAKONG_ACCOUNT = "soung_layhorth@trmc"
MERCHANT_NAME = "CV Generator Service"
MERCHANT_CITY = "Phnom Penh"
MERCHANT_PHONE = "85512345678"

# Pricing
CV_PRICES = {
    "normal": {"KHR": 1000, "USD": 0.50},
    "casino": {"KHR": 4000, "USD": 1.00}
}

# Game options for casino CV
GAME_OPTIONS = [
    "BACCARAT",
    "INSURANCE",
    "Tiger Dragon",
    "Niv Niv",
    "Roulette",
    "Blackjack",
    "Poker",
    "Slot Machine"
]

# Language texts
TEXTS = {
    "en": {
        "cv_type": "📋 *What type of CV?*\n\n🎰 *Casino CV*: For gaming positions (requires game knowledge)\n📄 *Normal CV*: For general positions",
        "name": "👤 *Full name?*\n\n📝 Format: Khmer / English\n💡 Example: ស៊ុន បូរ៉ / SOUN BORA",
        "address": "📍 *Current address?*\n\n💡 Example:\nVillage 3, Sangkat 3, Sihanouk ville",
        "phone": "📞 *Phone number?*\n\n💡 Example:\n• 097 9870 552\n• 012 345 678\n• +855 97 987 0552",
        "position": "💼 *Position you're applying for?*\n\n💡 Example: Dealer, Supervisor, etc.",
        "nationality": "🌍 *Nationality?*\n\n💡 Example: Khmer, Vietnamese, Chinese, etc.",
        "sex": "🚻 *Sex?*",
        "marital": "💍 *Marital status?*",
        "height": "📏 *Height?*\n\n💡 Examples:\n• 1.74m\n• 174cm\n• 5'9\"",
        "weight": "⚖️ *Weight?*\n\n💡 Examples:\n• 78kg\n• 78 kg\n• 172 lbs",
        "dob": "🎂 *Date of birth?*\n\n📝 Format: DD-MM-YYYY\n💡 Example: 28-01-1991",
        "pob": "🏠 *Place of birth?*\n\n💡 Example:\nKhoum Srong, Srok Prey Chor, Kompong Cham province, Cambodia",
        "photo": "📸 *Please send your photo*\n\n✅ Requirements:\n• Passport style photo\n• Formal attire (suit/tie)\n• Clear face, good lighting\n• Recent photo\n• Formats: JPG, JPEG, PNG",
        "id_card_front": "🪪 *Please send FRONT of your ID card*\n\n✅ Make sure:\n• Photo is clear and readable\n• All text is visible\n• No glare or shadows\n• Formats: JPG, JPEG, PNG",
        "id_card_back": "🪪 *Please send BACK of your ID card*\n\n✅ Make sure:\n• Photo is clear and readable\n• All text is visible\n• No glare or shadows\n• Formats: JPG, JPEG, PNG",
        "game": "🎮 *Select games you know*\n\nTap games below, then tap *Done ✅* when finished",
        "game_selected": "✅ *Selected:* {games}\n\nSelect more or tap *Done ✅*",
        "experience": "🧑‍💼 *Work experience?*\n\n📝 Format: YEAR-YEAR : Position duration\n\n💡 Example:\n2016-2020 : Working as seller 4 years\n2020-2022 : Working as CO at bank 2 years\n\n💭 Tip: List most recent first",
        "education": "🎓 *Education background?*\n\n📝 Format: YEAR-YEAR : School Grade\n\n💡 Example:\n2012-2015 : Kompong Cham High School Grade 12\n2009-2012 : Middle School Grade 9",
        "languages": "🗣 *Languages you speak?*\n\n📝 Format: Language : Level\n\n💡 Example:\nខ្មែរ Khmer : Mother Tongue\nអង់គ្លេស English : Fair\nចិន Chinese : Little\n\n💭 Levels: Mother Tongue, Fluent, Good, Fair, Little",
        "payment_currency": "💰 *Choose payment currency:*\n\n🏦 *KHR (Riel):* {khr_price:,} ៛\n💵 *USD (Dollar):* ${usd_price}\n\n✅ Proceed to payment",
        "payment_qr": "💳 *Scan QR Code to Pay*\n\n💰 *Amount:* {amount} {currency}\n📋 *Bill Number:* {bill_number}\n\n📱 *How to pay:*\n1. Open your banking app (ABA, ACLEDA, etc.)\n2. Scan this QR code\n3. Confirm the payment\n4. Tap *'I've Paid ✅'* button below\n\n⏱ QR code expires in 15 minutes",
        "payment_verifying": "⏳ *Verifying your payment...*\n\nPlease wait a moment...",
        "payment_success": "✅ *Payment Confirmed!*\n\n💰 Amount: {amount} {currency}\n📋 Receipt: {bill_number}\n⏰ Time: {time}\n\n🎉 Now creating your professional CV...",
        "payment_failed": "❌ *Payment Not Found*\n\n⚠️ We couldn't verify your payment yet.\n\n💡 *Please:*\n1. Make sure you completed the payment\n2. Wait 30 seconds and try again\n3. Contact support if issue persists\n\nTap *'Check Again 🔄'* to retry",
        "payment_expired": "⏰ *Payment Session Expired*\n\n❌ Your 15-minute payment window has expired.\n\n🔄 Type /start to create a new CV",
        "processing": "⏳ *Processing your CV...*\n\nPlease wait a moment...",
        "success": "✅ *Success!*\n\nYour professional CV has been created!\n\n📄 Check the document above\n💡 Open in browser to print\n\n🔄 Type /start to create another CV",
        "cancel": "❌ CV creation cancelled.\n\n🔄 Type /start to begin again",
        "invalid_phone": "⚠️ *Invalid phone number*\n\nPlease enter a valid format:\n• 012345678\n• +855123456789\n• 097 9870 552",
        "invalid_photo": "⚠️ *Please send a photo*\n\nMake sure you're sending an image file, not text",
        "cv_type_options": ["🎰 Casino CV", "📄 Normal CV"],
        "sex_options": ["Male", "Female"],
        "marital_options": ["Single", "Married", "Divorced", "Widowed"],
        "currency_options": ["🏦 Pay with KHR (Riel)", "💵 Pay with USD (Dollar)"],
    },
    "km": {
        "cv_type": "📋 *ប្រភេទ CV?*\n\n🎰 *CV កាស៊ីណូ*: សម្រាប់មុខតំណែងហ្គេម (ត្រូវការចំណេះដឹងហ្គេម)\n📄 *CV ធម្មតា*: សម្រាប់មុខតំណែងទូទៅ",
        "name": "👤 *ឈ្មោះពេញ?*\n\n📝 ទម្រង់: ខ្មែរ / អង់គ្លេស\n💡 ឧទាហរណ៍: ស៊ុន បូរ៉ / SOUN BORA",
        "address": "📍 *អាសយដ្ឋានបច្ចុប្បន្ន?*\n\n💡 ឧទាហរណ៍:\nភូមិ៣ សង្កាត់៣ ក្រុងព្រះសីហនុ",
        "phone": "📞 *លេខទូរស័ព្ទ?*\n\n💡 ឧទាហរណ៍:\n• 097 9870 552\n• 012 345 678\n• +855 97 987 0552",
        "position": "💼 *មុខតំណែងដែលចង់ដាក់ពាក្យ?*\n\n💡 ឧទាហរណ៍: ឌីលឺរ, ប៉ាត្រុង, ជជែក",
        "nationality": "🌍 *សញ្ជាតិ?*\n\n💡 ឧទាហរណ៍: ខ្មែរ, វៀតណាម, ចិន",
        "sex": "🚻 *ភេទ?*",
        "marital": "💍 *ស្ថានភាពអាពាហ៍ពិពាហ៍?*",
        "height": "📏 *កម្ពស់?*\n\n💡 ឧទាហរណ៍:\n• 1.74m\n• 174cm",
        "weight": "⚖️ *ទម្ងន់?*\n\n💡 ឧទាហរណ៍:\n• 78kg\n• 78 kg",
        "dob": "🎂 *ថ្ងៃខែឆ្នាំកំណើត?*\n\n📝 ទម្រង់: ថ្ងៃ-ខែ-ឆ្នាំ\n💡 ឧទាហរណ៍: 28-01-1991",
        "pob": "🏠 *ទីកន្លែងកំណើត?*\n\n💡 ឧទាហរណ៍:\nឃុំស្រង់ ស្រុកព្រៃជ័រ ខេត្តកំពង់ចាម ព្រះរាជាណាចក្រកម្ពុជា",
        "photo": "📸 *សូមផ្ញើរូបថតរបស់អ្នក*\n\n✅ តម្រូវការ:\n• រូបថតស្តាយល៍លិខិតឆ្លងដែន\n• ស្លៀកពាក់ឈុត/នឹកតៃ\n• មុខច្បាស់ ពន្លឺល្អ\n• រូបថតថ្មី\n• ទម្រង់: JPG, JPEG, PNG",
        "id_card_front": "🪪 *សូមផ្ញើរូបខាងមុខអត្តសញ្ញាណប័ណ្ណ*\n\n✅ ត្រូវប្រាកដថា:\n• រូបថតច្បាស់ អានបាន\n• អក្សរទាំងអស់មើលឃើញ\n• គ្មានពន្លឺឆ្លុះ ឬស្រមោល\n• ទម្រង់: JPG, JPEG, PNG",
        "id_card_back": "🪪 *សូមផ្ញើរូបខាងក្រោយអត្តសញ្ញាណប័ណ្ណ*\n\n✅ ត្រូវប្រាកដថា:\n• រូបថតច្បាស់ អានបាន\n• អក្សរទាំងអស់មើលឃើញ\n• គ្មានពន្លឺឆ្លុះ ឬស្រមោល\n• ទម្រង់: JPG, JPEG, PNG",
        "game": "🎮 *ជ្រើសរើសហ្គេមដែលអ្នកស្គាល់*\n\nចុចហ្គេមខាងក្រោម រួចចុច *រួចរាល់ ✅* នៅពេលបញ្ចប់",
        "game_selected": "✅ *បានជ្រើសរើស:* {games}\n\nជ្រើសរើសបន្ថែម ឬចុច *រួចរាល់ ✅*",
        "experience": "🧑‍💼 *បទពិសោធន៍ការងារ?*\n\n📝 ទម្រង់: ឆ្នាំ-ឆ្នាំ : មុខតំណែង រយៈពេល\n\n💡 ឧទាហរណ៍:\n2016-2020 : ធ្វើការជាអ្នកលក់ 4 ឆ្នាំ\n2020-2022 : ធ្វើការជា CO នៅធនាគារ 2 ឆ្នាំ\n\n💭 ដំបូន្មាន: ចុះថ្មីបំផុតមុនគេ",
        "education": "🎓 *កំរិតវប្បធម៌?*\n\n📝 ទម្រង់: ឆ្នាំ-ឆ្នាំ : សាលា ថ្នាក់\n\n💡 ឧទាហរណ៍:\n2012-2015 : វិទ្យាល័យកំពង់ចាម ថ្នាក់ទី១២\n2009-2012 : អនុវិទ្យាល័យ ថ្នាក់ទី៩",
        "languages": "🗣 *ភាសា?*\n\n📝 ទម្រង់: ភាសា : កម្រិត\n\n💡 ឧទាហរណ៍:\nខ្មែរ Khmer : Mother Tongue\nអង់គ្លេស English : Fair\nចិន Chinese : Little\n\n💭 កម្រិត: Mother Tongue, Fluent, Good, Fair, Little",
        "payment_currency": "💰 *ជ្រើសរើសរូបិយប័ណ្ណបង់ប្រាក់:*\n\n🏦 *KHR (រៀល):* {khr_price:,} ៛\n💵 *USD (ដុល្លារ):* ${usd_price}\n\n✅ បន្តទៅការបង់ប្រាក់",
        "payment_qr": "💳 *ស្កេន QR Code ដើម្បីបង់ប្រាក់*\n\n💰 *ចំនួនទឹកប្រាក់:* {amount} {currency}\n📋 *លេខវិក្កយបត្រ:* {bill_number}\n\n📱 *របៀបបង់ប្រាក់:*\n1. បើកកម្មវិធីធនាគាររបស់អ្នក (ABA, ACLEDA, ...)\n2. ស្កេន QR code នេះ\n3. បញ្ជាក់ការបង់ប្រាក់\n4. ចុចប៊ូតុង *'ខ្ញុំបានបង់ហើយ ✅'* ខាងក្រោម\n\n⏱ QR code នឹងផុតកំណត់ក្នុងរយៈពេល 15 នាទី",
        "payment_verifying": "⏳ *កំពុងផ្ទៀងផ្ទាត់ការបង់ប្រាក់...*\n\nសូមរង់ចាំបន្តិច...",
        "payment_success": "✅ *បានបញ្ជាក់ការបង់ប្រាក់!*\n\n💰 ចំនួនទឹកប្រាក់: {amount} {currency}\n📋 វិក្កយបត្រ: {bill_number}\n⏰ ពេលវេលា: {time}\n\n🎉 កំពុងបង្កើត CV របស់អ្នក...",
        "payment_failed": "❌ *រកមិនឃើញការបង់ប្រាក់*\n\n⚠️ យើងមិនអាចផ្ទៀងផ្ទាត់ការបង់ប្រាក់របស់អ្នកនៅឡើយទេ។\n\n💡 *សូម:*\n1. ត្រូវប្រាកដថាអ្នកបានបង់ប្រាក់រួចរាល់\n2. រង់ចាំ 30 វិនាទី ហើយព្យាយាមម្តងទៀត\n3. ទាក់ទងជំនួយ ប្រសិនបើបញ្ហានៅតែមាន\n\nចុច *'ពិនិត្យម្តងទៀត 🔄'* ដើម្បីព្យាយាមឡើងវិញ",
        "payment_expired": "⏰ *អស់ពេលបង់ប្រាក់*\n\n❌ រយៈពេល 15 នាទីសម្រាប់បង់ប្រាក់បានផុតកំណត់។\n\n🔄 វាយ /start ដើម្បីបង្កើត CV ថ្មី",
        "processing": "⏳ *កំពុងដំណើរការ CV របស់អ្នក...*\n\nសូមរង់ចាំបន្តិច...",
        "success": "✅ *ជោគជ័យ!*\n\nCV របស់អ្នកត្រូវបានបង្កើតហើយ!\n\n📄 ពិនិត្យឯកសារខាងលើ\n💡 បើកក្នុង browser ដើម្បីបោះពុម្ព\n\n🔄 វាយ /start ដើម្បីបង្កើត CV ថ្មី",
        "cancel": "❌ បានបោះបង់ការបង្កើត CV។\n\n🔄 វាយ /start ដើម្បីចាប់ផ្តើមម្តងទៀត",
        "invalid_phone": "⚠️ *លេខទូរស័ព្ទមិនត្រឹមត្រូវ*\n\nសូមបញ្ចូលទម្រង់ត្រឹមត្រូវ:\n• 012345678\n• +855123456789\n• 097 9870 552",
        "invalid_photo": "⚠️ *សូមផ្ញើរូបថត*\n\nត្រូវប្រាកដថាអ្នកផ្ញើរូបភាព មិនមែនអត្ថបទ",
        "cv_type_options": ["🎰 CV កាស៊ីណូ", "📄 CV ធម្មតា"],
        "sex_options": ["ប្រុស", "ស្រី"],
        "marital_options": ["នៅលីវ", "រៀបការ", "លែងលះ", "ម៉ាយ"],
        "currency_options": ["🏦 បង់ជាមួយ KHR (រៀល)", "💵 បង់ជាមួយ USD (ដុល្លារ)"],
    }
}


def get_text(lang, key):
    """Get text in specified language"""
    return TEXTS.get(lang, TEXTS["en"]).get(key, TEXTS["en"][key])


def validate_phone(phone):
    """Validate Cambodian phone number"""
    pattern = r'^(\+855|0)?[1-9]\d{7,9}$'
    return re.match(pattern, phone.strip())


def generate_bill_number():
    """Generate unique bill number"""
    return f"CV{datetime.now().strftime('%Y%m%d%H%M%S')}"


def compress_image(image_path, max_size_kb=300):
    """Compress image to reduce file size for embedding in HTML"""
    try:
        img = Image.open(image_path)
        
        # Convert RGBA to RGB if necessary
        if img.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
            img = background
        
        # Resize if too large
        max_dimension = 1200
        if max(img.size) > max_dimension:
            img.thumbnail((max_dimension, max_dimension), Image.Resampling.LANCZOS)
        
        # Compress to target size
        output = io.BytesIO()
        quality = 85
        
        while quality > 20:
            output.seek(0)
            output.truncate()
            img.save(output, format='JPEG', quality=quality, optimize=True)
            size_kb = output.tell() / 1024
            
            if size_kb <= max_size_kb:
                break
            quality -= 5
        
        # Save compressed image
        compressed_path = image_path.rsplit('.', 1)[0] + '_compressed.jpg'
        with open(compressed_path, 'wb') as f:
            f.write(output.getvalue())
        
        print(f"✓ Compressed {os.path.basename(image_path)}: {size_kb:.1f}KB (quality: {quality})")
        return compressed_path
        
    except Exception as e:
        print(f"⚠️ Error compressing image: {e}")
        return image_path


def create_payment_qr(cv_type, currency, bill_number):
    """Generate Bakong QR code for payment"""
    try:
        khqr = KHQR(BAKONG_TOKEN)
        
        amount = CV_PRICES[cv_type][currency]
        
        # Create QR string
        qr_string = khqr.create_qr(
            bank_account=BAKONG_ACCOUNT,
            merchant_name=MERCHANT_NAME,
            merchant_city=MERCHANT_CITY,
            amount=amount,
            currency=currency,
            store_label='CV Service',
            phone_number=MERCHANT_PHONE,
            bill_number=bill_number,
            terminal_label='Telegram-Bot',
            static=False
        )
        
        # Generate MD5 hash for payment verification
        md5_hash = khqr.generate_md5(qr_string)
        
        # Generate QR code image as PNG file
        qr_image_path = khqr.qr_image(qr_string)
        
        print(f"✓ QR Code generated successfully")
        print(f"  - Amount: {amount} {currency}")
        print(f"  - Bill: {bill_number}")
        print(f"  - MD5: {md5_hash}")
        print(f"  - Image: {qr_image_path}")
        
        return {
            'qr_image_path': qr_image_path,
            'qr_string': qr_string,
            'md5_hash': md5_hash,
            'amount': amount,
            'currency': currency,
            'bill_number': bill_number
        }
    except Exception as e:
        print(f"Error generating QR: {e}")
        import traceback
        traceback.print_exc()
        return None


def verify_payment(md5_hash):
    """Check if payment has been completed"""
    try:
        khqr = KHQR(BAKONG_TOKEN)
        payment_status = khqr.check_payment(md5_hash)
        
        print(f"🔍 Payment check - MD5: {md5_hash}, Status: {payment_status}")
        
        if payment_status == "PAID":
            payment_info = khqr.get_payment(md5_hash)
            print(f"✅ Payment verified: {payment_info}")
            return {
                'paid': True,
                'info': payment_info
            }
        return {'paid': False}
    except Exception as e:
        print(f"Error verifying payment: {e}")
        return {'paid': False}


def image_to_base64(image_path):
    """Convert image to base64 for embedding in HTML"""
    try:
        with open(image_path, 'rb') as img_file:
            return base64.b64encode(img_file.read()).decode('utf-8')
    except Exception as e:
        print(f"Error converting image: {e}")
        return None


def cleanup_images(data):
    """Delete all images after CV creation"""
    try:
        if data.get('photo_path') and os.path.exists(data['photo_path']):
            os.remove(data['photo_path'])
            print(f"✓ Deleted photo: {data['photo_path']}")
        
        if data.get('id_front_path') and os.path.exists(data['id_front_path']):
            os.remove(data['id_front_path'])
            print(f"✓ Deleted ID front: {data['id_front_path']}")
        
        if data.get('id_back_path') and os.path.exists(data['id_back_path']):
            os.remove(data['id_back_path'])
            print(f"✓ Deleted ID back: {data['id_back_path']}")
        
        # QR image is already deleted after sending to Telegram
        # No need to delete it again
        
        print("✓ All images cleaned up successfully")
    except Exception as e:
        print(f"⚠️ Error during cleanup: {e}")


def create_cv_html(data, lang):
    """Generate professional CV HTML with beautiful template design"""
    filename = f"CV_{data['name'].replace(' ', '_').replace('/', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
    filepath = os.path.join("cvs", filename)
    
    os.makedirs("cvs", exist_ok=True)
    
    # Compress and convert images to base64
    photo_base64 = ""
    if data.get('photo_path') and data['photo_path'] is not None:
        compressed_photo = compress_image(data['photo_path'], max_size_kb=300)
        photo_data = image_to_base64(compressed_photo)
        if photo_data:
            photo_base64 = f"data:image/jpeg;base64,{photo_data}"
        if compressed_photo != data['photo_path'] and os.path.exists(compressed_photo):
            os.remove(compressed_photo)
    
    id_front_base64 = ""
    if data.get('id_front_path') and data['id_front_path'] is not None:
        compressed_front = compress_image(data['id_front_path'], max_size_kb=300)
        id_data = image_to_base64(compressed_front)
        if id_data:
            id_front_base64 = f"data:image/jpeg;base64,{id_data}"
        if compressed_front != data['id_front_path'] and os.path.exists(compressed_front):
            os.remove(compressed_front)
    
    id_back_base64 = ""
    if data.get('id_back_path') and data['id_back_path'] is not None:
        compressed_back = compress_image(data['id_back_path'], max_size_kb=300)
        id_data = image_to_base64(compressed_back)
        if id_data:
            id_back_base64 = f"data:image/jpeg;base64,{id_data}"
        if compressed_back != data['id_back_path'] and os.path.exists(compressed_back):
            os.remove(compressed_back)
    
    # Parse work experience
    work_experience_items = []
    for line in data['experience'].split('\n'):
        if ':' in line and line.strip():
            parts = line.split(':', 1)
            years = parts[0].strip()
            description = parts[1].strip()
            
            year_match = re.search(r'(\d{4})\s*-\s*(\d{4})', years)
            if year_match:
                start_year = year_match.group(1)
                end_year = year_match.group(2)
                duration = int(end_year) - int(start_year)
                work_experience_items.append({
                    'years': f"{start_year} - {end_year}",
                    'duration': f"{duration} years",
                    'description': description
                })
    
    # Parse education
    education_items = []
    for line in data['education'].split('\n'):
        if ':' in line and line.strip():
            parts = line.split(':', 1)
            years = parts[0].strip()
            description = parts[1].strip()
            education_items.append({
                'years': years,
                'description': description
            })
    
    # Parse languages with levels
    languages_items = []
    language_levels = {'Mother Tongue': 100, 'Fluent': 90, 'Good': 75, 'Fair': 60, 'Little': 25}
    for line in data['languages'].split('\n'):
        if ':' in line and line.strip():
            parts = line.split(':', 1)
            language = parts[0].strip()
            level = parts[1].strip()
            width = language_levels.get(level, 50)
            languages_items.append({
                'language': language,
                'level': level,
                'width': width
            })
    
    # Game knowledge section (only for casino)
    game_section = ""
    if data['cv_type'] == 'casino' and data.get('game'):
        game_title = "ចំណេះដឹងហ្គេម GAME KNOWLEDGE" if lang == 'km' else "GAME KNOWLEDGE"
        game_section = f'''
        <!-- Game Knowledge -->
        <div class="px-8 pb-8">
            <h3 class="text-xl font-bold text-cyan-600 mb-4 pb-2 border-b-2 border-cyan-600">
                <span class="khmer-text">{game_title}</span>
            </h3>
            <div class="bg-gradient-to-r from-cyan-50 to-blue-50 p-5 rounded-lg border border-cyan-200">
                <p class="text-gray-700">{data['game']}</p>
            </div>
        </div>
        '''
    
    # ID Card section (only show if at least one ID is provided)
    id_card_page = ""
    if (data.get('id_front_path') and data['id_front_path'] is not None) or (data.get('id_back_path') and data['id_back_path'] is not None):
        id_card_page = f'''
    <!-- PAGE 3: ID Card -->
    <div class="page">
        <div class="bg-gradient-to-r from-cyan-500 to-blue-500 p-6 text-white text-center">
            <h2 class="text-2xl font-bold khmer-text">{data['name']}</h2>
            <p class="text-sm mt-1">Curriculum Vitae</p>
        </div>

        <div class="p-8">
            <h3 class="text-xl font-bold text-cyan-600 mb-4 pb-2 border-b-2 border-cyan-600">
                <span class="khmer-text">{"អត្តសញ្ញាណប័ណ្ណ" if lang == 'km' else ""}</span>
                {"<br>" if lang == 'km' else ""}
                <span class="text-sm">KHMER IDENTITY CARD</span>
            </h3>
            
            <div class="space-y-6">
                {f'''<div class="bg-gradient-to-br from-gray-50 to-cyan-50 p-4 rounded-lg border-2 border-cyan-200 shadow-md">
                    <p class="text-sm text-cyan-700 mb-3 font-bold text-center">FRONT SIDE / {"ផ្នែកមុខ" if lang == 'km' else ""}</p>
                    <div class="bg-white p-2 rounded shadow-inner">
                        <img src="{id_front_base64}" alt="ID Card Front" class="w-full h-auto rounded">
                    </div>
                </div>''' if id_front_base64 else ''}

                {f'''<div class="bg-gradient-to-br from-gray-50 to-cyan-50 p-4 rounded-lg border-2 border-cyan-200 shadow-md">
                    <p class="text-sm text-cyan-700 mb-3 font-bold text-center">BACK SIDE / {"ផ្នែកក្រោយ" if lang == 'km' else ""}</p>
                    <div class="bg-white p-2 rounded shadow-inner">
                        <img src="{id_back_base64}" alt="ID Card Back" class="w-full h-auto rounded">
                    </div>
                </div>''' if id_back_base64 else ''}
            </div>
        </div>

        <div class="absolute bottom-0 left-0 right-0 bg-gradient-to-r from-cyan-500 to-blue-500 p-3 text-white text-center text-xs">
            <p class="font-semibold">Page 3 of 4</p>
        </div>
    </div>
        '''
    
    # Determine page numbers based on whether ID card page exists
    page_4_number = "4 of 4" if id_card_page else "3 of 3"
    
    # Additional contact row for casino position
    casino_contact_row = ""
    if data['cv_type'] == 'casino' and data.get('position'):
        casino_contact_row = f'''
            <tr class="border-b-4 border-black">
                <td class="p-5 font-bold khmer-text border-r-4 border-black bg-gray-100 text-base" style="width: 40%">
                    ស្នើសុំ / APPLY
                </td>
                <td class="p-5 text-base">
                    {data.get('position', '')}
                </td>
            </tr>
        '''
    
    # Determine total number of pages
    total_pages = 3 if id_card_page else 2
    total_pages_text = f"{total_pages + 1} Pages"  # +1 for contact page
    
    html_content = f'''<!DOCTYPE html>
<html lang="km">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CV - {data['name']}</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Noto+Serif+Khmer:wght@400;600;700&family=Roboto:wght@400;500;700&display=swap');
        
        body {{
            font-family: 'Roboto', 'Noto Serif Khmer', sans-serif;
        }}
        
        .khmer-text {{
            font-family: 'Noto Serif Khmer', serif;
        }}
        
        @page {{
            size: A4;
            margin: 0;
        }}
        
        @media print {{
            body {{
                print-color-adjust: exact;
                -webkit-print-color-adjust: exact;
                margin: 0;
                padding: 0;
            }}
            .page {{
                page-break-after: always;
                box-shadow: none;
            }}
            .page:last-child {{
                page-break-after: auto;
            }}
            .no-print {{
                display: none;
            }}
        }}
        
        .page {{
            width: 210mm;
            min-height: 297mm;
            margin: 0 auto 20px;
            background: white;
            position: relative;
        }}
        
        @media screen {{
            .page {{
                box-shadow: 0 0 20px rgba(0,0,0,0.1);
            }}
        }}

        .cut-line {{
            border-top: 2px dashed #999;
            position: relative;
        }}
        
        .cut-line::before {{
            content: '✂ CUT HERE';
            position: absolute;
            top: -12px;
            left: 50%;
            transform: translateX(-50%);
            background: white;
            padding: 0 10px;
            font-size: 10px;
            color: #999;
            font-weight: bold;
        }}
        
        .photo-4x6 {{
            width: 4cm;
            height: 6cm;
        }}
    </style>
</head>
<body class="bg-gray-200">
    <div class="no-print fixed top-4 right-4 z-50">
        <button onclick="window.print()" class="bg-cyan-600 hover:bg-cyan-700 text-white px-6 py-3 rounded-lg shadow-lg flex items-center gap-2">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z"/>
            </svg>
            Print CV ({total_pages_text})
        </button>
    </div>

    <!-- PAGE 1: Header and Main Info -->
    <div class="page">
        <div class="bg-gradient-to-r from-cyan-500 to-blue-500 p-8 text-white">
            <div class="flex flex-col items-center gap-4">
                <div class="photo-4x6 bg-white rounded-lg overflow-hidden border-4 border-white shadow-lg flex-shrink-0">
                    {f'<img src="{photo_base64}" alt="Photo" class="w-full h-full object-cover">' if photo_base64 else '''
                    <div class="w-full h-full flex flex-col items-center justify-center text-gray-400 border-4 border-dashed border-gray-300">
                        <svg class="w-16 h-16" fill="currentColor" viewBox="0 0 20 20">
                            <path fill-rule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clip-rule="evenodd"/>
                        </svg>
                        <p class="text-xs mt-2">4x6 Photo</p>
                    </div>
                    '''}
                </div>
                <div class="text-center">
                    <h1 class="text-3xl font-bold mb-2">CURRICULUM VITAE</h1>
                    <h2 class="text-xl khmer-text mb-1">{data['name']}</h2>
                    <div class="flex flex-col gap-2 mt-3 text-sm">
                        {f'''<div class="flex items-center gap-2 justify-center">
                            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"/>
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"/>
                            </svg>
                            <span>{data['address']}</span>
                        </div>''' if data.get('address') and data['address'].strip() else ''}
                        <div class="flex items-center gap-2 justify-center">
                            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"/>
                            </svg>
                            <span class="font-semibold">{data['phone']}</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <div class="p-8">
            <h3 class="text-xl font-bold text-cyan-600 mb-4 pb-2 border-b-2 border-cyan-600">
                <span class="khmer-text">{"ព័ត៌មានផ្ទាល់ខ្លួន" if lang == 'km' else ""}</span>
                {"<br>" if lang == 'km' else ""}
                <span class="text-sm">PERSONAL INFORMATION</span>
            </h3>
            <div class="grid grid-cols-2 gap-4 text-sm">
                <div>
                    <p class="font-semibold text-gray-700 khmer-text mb-1">{"សញ្ជាតិ / " if lang == 'km' else ""}Nationality</p>
                    <p class="text-gray-600 bg-gray-50 p-2 rounded">{data['nationality']}</p>
                </div>
                <div>
                    <p class="font-semibold text-gray-700 khmer-text mb-1">{"ភេទ / " if lang == 'km' else ""}Sex</p>
                    <p class="text-gray-600 bg-gray-50 p-2 rounded">{data['sex']}</p>
                </div>
                <div>
                    <p class="font-semibold text-gray-700 khmer-text mb-1">{"ស្ថានភាពគ្រួសារ / " if lang == 'km' else ""}Marital Status</p>
                    <p class="text-gray-600 bg-gray-50 p-2 rounded">{data['marital']}</p>
                </div>
                <div>
                    <p class="font-semibold text-gray-700 khmer-text mb-1">{"កម្ពស់ / " if lang == 'km' else ""}Height</p>
                    <p class="text-gray-600 bg-gray-50 p-2 rounded">{data['height']}</p>
                </div>
                <div>
                    <p class="font-semibold text-gray-700 khmer-text mb-1">{"ទម្ងន់ / " if lang == 'km' else ""}Weight</p>
                    <p class="text-gray-600 bg-gray-50 p-2 rounded">{data['weight']}</p>
                </div>
                <div>
                    <p class="font-semibold text-gray-700 khmer-text mb-1">{"ថ្ងៃខែឆ្នាំកំណើត / " if lang == 'km' else ""}Date of Birth</p>
                    <p class="text-gray-600 bg-gray-50 p-2 rounded">{data['dob']}</p>
                </div>
                <div class="col-span-2">
                    <p class="font-semibold text-gray-700 khmer-text mb-1">{"ទីកន្លែងកំណើត / " if lang == 'km' else ""}Place of Birth</p>
                    <p class="text-gray-600 bg-gray-50 p-2 rounded">{data['pob']}</p>
                </div>
            </div>
        </div>

        <div class="px-8 pb-8">
            <h3 class="text-xl font-bold text-cyan-600 mb-4 pb-2 border-b-2 border-cyan-600">
                <span class="khmer-text">{"ភាសា" if lang == 'km' else ""}</span>
                {"<br>" if lang == 'km' else ""}
                <span class="text-sm">LANGUAGES</span>
            </h3>
            <div class="space-y-4">
                {"".join([f'''
                <div>
                    <div class="flex justify-between mb-2">
                        <span class="font-semibold khmer-text text-gray-700">{item['language']}</span>
                        <span class="text-sm text-cyan-600 font-semibold">{item['level']}</span>
                    </div>
                    <div class="w-full bg-gray-200 rounded-full h-3">
                        <div class="bg-gradient-to-r from-cyan-500 to-blue-500 h-3 rounded-full" style="width: {item['width']}%"></div>
                    </div>
                </div>
                ''' for item in languages_items])}
            </div>
        </div>

        <div class="absolute bottom-0 left-0 right-0 bg-gradient-to-r from-cyan-500 to-blue-500 p-3 text-white text-center text-xs">
            <p class="font-semibold">Page 1 of 4</p>
        </div>
    </div>

    <!-- PAGE 2: Work Experience and Education -->
    <div class="page">
        <div class="bg-gradient-to-r from-cyan-500 to-blue-500 p-6 text-white text-center">
            <h2 class="text-2xl font-bold khmer-text">{data['name']}</h2>
            <p class="text-sm mt-1">Curriculum Vitae</p>
        </div>

        <div class="p-8">
            <h3 class="text-xl font-bold text-cyan-600 mb-4 pb-2 border-b-2 border-cyan-600">
                <span class="khmer-text">{"បទពិសោធន៍ការងារ" if lang == 'km' else ""}</span>
                {"<br>" if lang == 'km' else ""}
                <span class="text-sm">WORK EXPERIENCE</span>
            </h3>
            <div class="space-y-6">
                {"".join([f'''
                <div class="relative pl-8 border-l-4 border-cyan-500">
                    <div class="absolute -left-2.5 top-2 w-4 h-4 bg-cyan-500 rounded-full border-2 border-white"></div>
                    <div class="bg-gradient-to-r from-cyan-50 to-blue-50 p-5 rounded-lg border border-cyan-200">
                        <div class="flex items-center gap-2 mb-2">
                            <span class="bg-cyan-600 text-white text-xs px-3 py-1 rounded-full font-semibold">{item['years']}</span>
                            <span class="text-xs text-gray-500">{item['duration']}</span>
                        </div>
                        <h4 class="text-lg font-bold text-gray-800 mb-2">{item['description'].split(' ', 3)[0] + ' ' + item['description'].split(' ', 3)[1] + ' ' + item['description'].split(' ', 3)[2] if len(item['description'].split()) > 2 else item['description']}</h4>
                        <p class="text-sm text-gray-600">{item['description']}</p>
                    </div>
                </div>
                ''' for item in reversed(work_experience_items)])}
            </div>
        </div>

        {game_section}

        <div class="px-8 pb-8">
            <h3 class="text-xl font-bold text-cyan-600 mb-4 pb-2 border-b-2 border-cyan-600">
                <span class="khmer-text">{"ប្រវត្តិសិក្សា" if lang == 'km' else ""}</span>
                {"<br>" if lang == 'km' else ""}
                <span class="text-sm">EDUCATION BACKGROUND</span>
            </h3>
            <div class="space-y-6">
                {"".join([f'''
                <div class="relative pl-8 border-l-4 border-cyan-500">
                    <div class="absolute -left-2.5 top-2 w-4 h-4 bg-cyan-500 rounded-full border-2 border-white"></div>
                    <div class="bg-gradient-to-r from-cyan-50 to-blue-50 p-5 rounded-lg border border-cyan-200">
                        <div class="flex items-center gap-2 mb-2">
                            <span class="bg-cyan-600 text-white text-xs px-3 py-1 rounded-full font-semibold">{item['years']}</span>
                        </div>
                        <h4 class="text-lg font-bold text-gray-800 mb-2">{item['description'].split(' Grade')[0] if 'Grade' in item['description'] else item['description']}</h4>
                        <p class="text-sm text-gray-600">{item['description']}</p>
                    </div>
                </div>
                ''' for item in education_items])}
            </div>
        </div>

        <div class="absolute bottom-0 left-0 right-0 bg-gradient-to-r from-cyan-500 to-blue-500 p-3 text-white text-center text-xs">
            <p class="font-semibold">Page 2 of 4</p>
        </div>
    </div>

    {id_card_page}

    <!-- PAGE 4: Contact Information -->
    <div class="page flex items-center justify-center">
        <div class="w-full p-8">
            <div class="text-center mb-8">
                <div class="bg-yellow-50 border-2 border-yellow-300 rounded-lg p-4 inline-block">
                    <p class="text-sm font-bold text-yellow-800 mb-2">
                        ✂️ INSTRUCTIONS / {"សេចក្តីណែនាំ" if lang == 'km' else ""}
                    </p>
                    <p class="text-xs text-yellow-700">
                        Cut along the dotted lines below and glue to the outside of your document<br>
                        <span class="khmer-text">{"កាត់តាមបន្ទាត់ចុចខាងក្រោម ហើយបិទនៅខាងក្រៅឯកសាររបស់អ្នក" if lang == 'km' else ""}</span>
                    </p>
                </div>
            </div>

            <div class="cut-line mb-4"></div>

            <div class="max-w-3xl mx-auto">
                <div class="mb-4">
                    <h3 class="text-2xl font-bold text-cyan-600 khmer-text text-center">
                        {"ព័ត៌មានទំនាក់ទំនង" if lang == 'km' else "Contact Information"}
                    </h3>
                    <p class="text-center text-sm text-gray-600 mt-1">CONTACT INFORMATION</p>
                </div>
                
                <div class="border-4 border-black rounded-lg overflow-hidden shadow-lg">
                    <table class="w-full">
                        <tbody>
                            <tr class="border-b-4 border-black">
                                <td class="p-5 font-bold khmer-text border-r-4 border-black bg-gray-100 text-base" style="width: 40%">
                                    ឈ្មោះ / NAME
                                </td>
                                <td class="p-5 khmer-text font-semibold text-base">
                                    {data['name']}
                                </td>
                            </tr>
                            {casino_contact_row}
                            {f'''<tr class="border-b-4 border-black">
                                <td class="p-5 font-bold khmer-text border-r-4 border-black bg-gray-100 text-base">
                                    អាសយដ្ឋាន / ADDRESS
                                </td>
                                <td class="p-5 text-base">
                                    {data['address']}
                                </td>
                            </tr>''' if data.get('address') and data['address'].strip() else ''}
                            <tr>
                                <td class="p-5 font-bold khmer-text border-r-4 border-black bg-gray-100 text-base">
                                    លេខទូរស័ព្ទ / PHONE NUMBER
                                </td>
                                <td class="p-5 font-bold text-cyan-600 text-xl">
                                    {data['phone']}
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>

            <div class="cut-line mt-4"></div>

            <div class="text-center mt-8">
                <div class="bg-gray-100 border border-gray-300 rounded-lg p-3 inline-block">
                    <p class="text-xs text-gray-600">
                        💡 <span class="font-semibold">Tip:</span> Use glue stick or double-sided tape for best results<br>
                        <span class="khmer-text">{"គន្លឹះ៖ ប្រើកាវដំបងឬកាវ២ផ្នែកសម្រាប់លទ្ធផលល្អបំផុត" if lang == 'km' else ""}</span>
                    </p>
                </div>
            </div>
        </div>

        <div class="absolute bottom-0 left-0 right-0 bg-gradient-to-r from-cyan-500 to-blue-500 p-4 text-white text-center">
            <p class="font-semibold text-sm">Page {page_4_number} - Contact Information (For Cutting)</p>
            <p class="text-xs mt-2 opacity-90">© {datetime.now().year} {data['name']} - Curriculum Vitae | Kingdom of Cambodia | ព្រះរាជាណាចក្រកម្ពុជា</p>
        </div>
    </div>
</body>
</html>
    '''
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    return filepath


# Handler functions
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["English 🇬🇧", "ខ្មែរ 🇰🇭"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text(
        "👋 *Welcome to Professional CV Generator!*\nសូមស្វាគមន៍មកកាន់ CV Generator!\n\n🌍 Please choose your language:\nសូមជ្រើសរើសភាសា:",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
    return LANGUAGE


async def language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    choice = update.message.text
    if "English" in choice or "🇬🇧" in choice:
        context.user_data["language"] = "en"
    else:
        context.user_data["language"] = "km"
    
    lang = context.user_data["language"]
    keyboard = [[opt] for opt in get_text(lang, "cv_type_options")]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text(
        get_text(lang, "cv_type"),
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
    return CV_TYPE


async def cv_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    choice = update.message.text
    lang = context.user_data.get("language", "en")
    
    if "Casino" in choice or "កាស៊ីណូ" in choice:
        context.user_data["cv_type"] = "casino"
    else:
        context.user_data["cv_type"] = "normal"
    
    await update.message.reply_text(
        get_text(lang, "name"),
        reply_markup=ReplyKeyboardRemove(),
        parse_mode='Markdown'
    )
    return NAME


async def name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["name"] = update.message.text
    lang = context.user_data.get("language", "en")
    
    # Add skip button for address
    keyboard = [["⏭️ Skip Address" if lang == "en" else "⏭️ រំលងអាសយដ្ឋាន"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    
    await update.message.reply_text(
        get_text(lang, "address"), 
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
    return ADDRESS


async def address(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Check if user clicked skip button
    if "Skip" in update.message.text or "រំលង" in update.message.text:
        context.user_data["address"] = ""
    else:
        context.user_data["address"] = update.message.text
    
    lang = context.user_data.get("language", "en")
    await update.message.reply_text(
        get_text(lang, "phone"), 
        reply_markup=ReplyKeyboardRemove(),
        parse_mode='Markdown'
    )
    return PHONE


async def phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    phone = update.message.text
    lang = context.user_data.get("language", "en")
    
    if not validate_phone(phone):
        await update.message.reply_text(get_text(lang, "invalid_phone"), parse_mode='Markdown')
        return PHONE
    
    context.user_data["phone"] = phone
    
    if context.user_data.get("cv_type") == "casino":
        await update.message.reply_text(get_text(lang, "position"), parse_mode='Markdown')
        return POSITION
    else:
        await update.message.reply_text(get_text(lang, "nationality"), parse_mode='Markdown')
        return NATIONALITY


async def position(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["position"] = update.message.text
    lang = context.user_data.get("language", "en")
    await update.message.reply_text(get_text(lang, "nationality"), parse_mode='Markdown')
    return NATIONALITY


async def nationality(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["nationality"] = update.message.text
    lang = context.user_data.get("language", "en")
    keyboard = [[opt] for opt in get_text(lang, "sex_options")]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text(get_text(lang, "sex"), reply_markup=reply_markup, parse_mode='Markdown')
    return SEX


async def sex(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["sex"] = update.message.text
    lang = context.user_data.get("language", "en")
    keyboard = [[opt] for opt in get_text(lang, "marital_options")]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text(get_text(lang, "marital"), reply_markup=reply_markup, parse_mode='Markdown')
    return MARITAL


async def marital(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["marital"] = update.message.text
    lang = context.user_data.get("language", "en")
    await update.message.reply_text(get_text(lang, "height"), reply_markup=ReplyKeyboardRemove(), parse_mode='Markdown')
    return HEIGHT


async def height(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["height"] = update.message.text
    lang = context.user_data.get("language", "en")
    await update.message.reply_text(get_text(lang, "weight"), parse_mode='Markdown')
    return WEIGHT


async def weight(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["weight"] = update.message.text
    lang = context.user_data.get("language", "en")
    await update.message.reply_text(get_text(lang, "dob"), parse_mode='Markdown')
    return DOB


async def dob(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["dob"] = update.message.text
    lang = context.user_data.get("language", "en")
    await update.message.reply_text(get_text(lang, "pob"), parse_mode='Markdown')
    return POB


async def pob(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["pob"] = update.message.text
    lang = context.user_data.get("language", "en")
    
    # Add skip button for photo
    keyboard = [["⏭️ Skip Photo" if lang == "en" else "⏭️ រំលងរូបថត"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    
    await update.message.reply_text(
        get_text(lang, "photo"), 
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
    return PHOTO


async def photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = context.user_data.get("language", "en")
    
    # Check if user clicked skip button
    if update.message.text and ("Skip" in update.message.text or "រំលង" in update.message.text):
        context.user_data["photo_path"] = None
        
        # Add skip button for ID card front
        keyboard = [["⏭️ Skip ID Cards" if lang == "en" else "⏭️ រំលងអត្តសញ្ញាណប័ណ្ណ"]]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        
        await update.message.reply_text(
            get_text(lang, "id_card_front"), 
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        return ID_CARD_FRONT
    
    if not update.message.photo and not update.message.document:
        await update.message.reply_text(get_text(lang, "invalid_photo"), parse_mode='Markdown')
        return PHOTO
    
    if update.message.photo:
        photo_file = await update.message.photo[-1].get_file()
        file_ext = "jpg"
    elif update.message.document and update.message.document.mime_type in ['image/png', 'image/jpeg', 'image/jpg']:
        photo_file = await update.message.document.get_file()
        file_ext = update.message.document.file_name.split('.')[-1].lower()
    else:
        await update.message.reply_text(get_text(lang, "invalid_photo"), parse_mode='Markdown')
        return PHOTO
    
    photo_path = f"photos/photo_{update.effective_user.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{file_ext}"
    os.makedirs("photos", exist_ok=True)
    await photo_file.download_to_drive(photo_path)
    context.user_data["photo_path"] = photo_path
    
    # Add skip button for ID card front
    keyboard = [["⏭️ Skip ID Cards" if lang == "en" else "⏭️ រំលងអត្តសញ្ញាណប័ណ្ណ"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    
    await update.message.reply_text(
        get_text(lang, "id_card_front"), 
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
    return ID_CARD_FRONT


async def id_card_front(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = context.user_data.get("language", "en")
    
    # Check if user clicked skip button
    if update.message.text and ("Skip" in update.message.text or "រំលង" in update.message.text):
        context.user_data["id_front_path"] = None
        context.user_data["id_back_path"] = None
        
        # Skip directly to appropriate next step
        if context.user_data.get("cv_type") == "casino":
            context.user_data["selected_games"] = []
            keyboard = []
            for i in range(0, len(GAME_OPTIONS), 2):
                row = GAME_OPTIONS[i:i+2]
                keyboard.append(row)
            keyboard.append(["Done ✅" if lang == "en" else "រួចរាល់ ✅"])
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
            await update.message.reply_text(
                get_text(lang, "game"), 
                reply_markup=reply_markup, 
                parse_mode='Markdown'
            )
            return GAME
        else:
            await update.message.reply_text(
                get_text(lang, "experience"), 
                reply_markup=ReplyKeyboardRemove(),
                parse_mode='Markdown'
            )
            return EXPERIENCE
    
    if not update.message.photo and not update.message.document:
        await update.message.reply_text(get_text(lang, "invalid_photo"), parse_mode='Markdown')
        return ID_CARD_FRONT
    
    if update.message.photo:
        id_file = await update.message.photo[-1].get_file()
        file_ext = "jpg"
    elif update.message.document and update.message.document.mime_type in ['image/png', 'image/jpeg', 'image/jpg']:
        id_file = await update.message.document.get_file()
        file_ext = update.message.document.file_name.split('.')[-1].lower()
    else:
        await update.message.reply_text(get_text(lang, "invalid_photo"), parse_mode='Markdown')
        return ID_CARD_FRONT
    
    id_path = f"ids/id_front_{update.effective_user.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{file_ext}"
    os.makedirs("ids", exist_ok=True)
    await id_file.download_to_drive(id_path)
    context.user_data["id_front_path"] = id_path
    
    await update.message.reply_text(
        get_text(lang, "id_card_back"), 
        reply_markup=ReplyKeyboardRemove(),
        parse_mode='Markdown'
    )
    return ID_CARD_BACK


async def id_card_back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = context.user_data.get("language", "en")
    
    if not update.message.photo and not update.message.document:
        await update.message.reply_text(get_text(lang, "invalid_photo"), parse_mode='Markdown')
        return ID_CARD_BACK
    
    if update.message.photo:
        id_file = await update.message.photo[-1].get_file()
        file_ext = "jpg"
    elif update.message.document and update.message.document.mime_type in ['image/png', 'image/jpeg', 'image/jpg']:
        id_file = await update.message.document.get_file()
        file_ext = update.message.document.file_name.split('.')[-1].lower()
    else:
        await update.message.reply_text(get_text(lang, "invalid_photo"), parse_mode='Markdown')
        return ID_CARD_BACK
    
    id_path = f"ids/id_back_{update.effective_user.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{file_ext}"
    os.makedirs("ids", exist_ok=True)
    await id_file.download_to_drive(id_path)
    context.user_data["id_back_path"] = id_path
    
    if context.user_data.get("cv_type") == "casino":
        context.user_data["selected_games"] = []
        keyboard = []
        for i in range(0, len(GAME_OPTIONS), 2):
            row = GAME_OPTIONS[i:i+2]
            keyboard.append(row)
        keyboard.append(["Done ✅" if lang == "en" else "រួចរាល់ ✅"])
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text(get_text(lang, "game"), reply_markup=reply_markup, parse_mode='Markdown')
        return GAME
    else:
        await update.message.reply_text(get_text(lang, "experience"), parse_mode='Markdown')
        return EXPERIENCE


async def game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = context.user_data.get("language", "en")
    choice = update.message.text
    
    if "Done" in choice or "រួចរាល់" in choice:
        if not context.user_data.get("selected_games"):
            await update.message.reply_text("⚠️ Please select at least one game!", parse_mode='Markdown')
            return GAME
        
        context.user_data["game"] = ", ".join(context.user_data["selected_games"])
        await update.message.reply_text(get_text(lang, "experience"), reply_markup=ReplyKeyboardRemove(), parse_mode='Markdown')
        return EXPERIENCE
    
    if choice not in context.user_data["selected_games"]:
        context.user_data["selected_games"].append(choice)
    
    selected_text = get_text(lang, "game_selected").format(games=", ".join(context.user_data["selected_games"]))
    keyboard = []
    for i in range(0, len(GAME_OPTIONS), 2):
        row = GAME_OPTIONS[i:i+2]
        keyboard.append(row)
    keyboard.append(["Done ✅" if lang == "en" else "រួចរាល់ ✅"])
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(selected_text, reply_markup=reply_markup, parse_mode='Markdown')
    return GAME


async def experience(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["experience"] = update.message.text
    lang = context.user_data.get("language", "en")
    await update.message.reply_text(get_text(lang, "education"), parse_mode='Markdown')
    return EDUCATION


async def education(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["education"] = update.message.text
    lang = context.user_data.get("language", "en")
    await update.message.reply_text(get_text(lang, "languages"), parse_mode='Markdown')
    return LANGUAGES


async def languages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["languages"] = update.message.text
    lang = context.user_data.get("language", "en")
    
    # Check if user is admin - skip payment
    if update.effective_user.id == ADMIN_ID:
        await update.message.reply_text(
            "🔓 *Admin Access Detected*\n\nSkipping payment process...\n\n⏳ Creating your CV now...",
            parse_mode='Markdown'
        )
        
        # Generate CV immediately
        await asyncio.sleep(1)
        html_path = create_cv_html(context.user_data, lang)
        
        file_size_mb = os.path.getsize(html_path) / (1024 * 1024)
        print(f"✓ Admin CV file size: {file_size_mb:.2f} MB")
        
        with open(html_path, 'rb') as html_file:
            await update.message.reply_document(
                document=html_file,
                filename=os.path.basename(html_path),
                caption=get_text(lang, "success"),
                parse_mode='Markdown'
            )
        
        cleanup_images(context.user_data)
        context.user_data.clear()
        return ConversationHandler.END
    
    # Regular users - show payment options
    cv_type = context.user_data.get("cv_type", "normal")
    khr_price = CV_PRICES[cv_type]['KHR']
    usd_price = CV_PRICES[cv_type]['USD']
    
    keyboard = [[opt] for opt in get_text(lang, "currency_options")]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    
    message_text = get_text(lang, "payment_currency").format(
        khr_price=khr_price,
        usd_price=usd_price
    )
    
    await update.message.reply_text(
        message_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
    return PAYMENT_CURRENCY


async def payment_currency(update: Update, context: ContextTypes.DEFAULT_TYPE):
    choice = update.message.text
    lang = context.user_data.get("language", "en")
    
    if "KHR" in choice or "រៀល" in choice:
        currency = "KHR"
    else:
        currency = "USD"
    
    cv_type = context.user_data.get("cv_type", "normal")
    bill_number = generate_bill_number()
    
    await update.message.reply_text(
        "⏳ Generating QR code..." if lang == "en" else "⏳ កំពុងបង្កើត QR code...",
        reply_markup=ReplyKeyboardRemove()
    )
    
    payment_data = create_payment_qr(cv_type, currency, bill_number)
    
    if not payment_data:
        await update.message.reply_text(
            "❌ Error generating payment QR. Please contact support.",
            reply_markup=ReplyKeyboardRemove()
        )
        cleanup_images(context.user_data)
        context.user_data.clear()
        return ConversationHandler.END
    
    context.user_data["payment"] = payment_data
    context.user_data["payment_time"] = datetime.now()
    
    keyboard = [
        [InlineKeyboardButton(
            "✅ I've Paid" if lang == "en" else "✅ ខ្ញុំបានបង់ហើយ", 
            callback_data="verify_payment"
        )],
        [InlineKeyboardButton(
            "❌ Cancel" if lang == "en" else "❌ បោះបង់", 
            callback_data="cancel_payment"
        )]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    amount_display = f"{payment_data['amount']:,}" if currency == "KHR" else f"${payment_data['amount']}"
    message_text = get_text(lang, "payment_qr").format(
        amount=amount_display,
        currency=currency,
        bill_number=bill_number
    )
    
    # Send QR code image
    with open(payment_data['qr_image_path'], 'rb') as qr_file:
        await update.message.reply_photo(
            photo=qr_file,
            caption=message_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    # Delete QR image immediately after sending
    try:
        if os.path.exists(payment_data['qr_image_path']):
            os.remove(payment_data['qr_image_path'])
            print(f"✓ Deleted QR image immediately: {payment_data['qr_image_path']}")
    except Exception as e:
        print(f"⚠️ Error deleting QR image: {e}")
    
    return PAYMENT_VERIFICATION


async def verify_payment_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    lang = context.user_data.get("language", "en")
    
    payment_time = context.user_data.get("payment_time")
    if payment_time and (datetime.now() - payment_time).seconds > 900:
        await query.edit_message_caption(
            caption=get_text(lang, "payment_expired"),
            parse_mode='Markdown'
        )
        cleanup_images(context.user_data)
        context.user_data.clear()
        return ConversationHandler.END
    
    await query.edit_message_caption(
        caption=get_text(lang, "payment_verifying"),
        parse_mode='Markdown'
    )
    
    await asyncio.sleep(3)
    
    payment_data = context.user_data.get("payment")
    result = verify_payment(payment_data['md5_hash'])
    
    if result['paid']:
        amount_display = f"{payment_data['amount']:,}" if payment_data['currency'] == "KHR" else f"${payment_data['amount']}"
        success_msg = get_text(lang, "payment_success").format(
            amount=amount_display,
            currency=payment_data['currency'],
            bill_number=payment_data['bill_number'],
            time=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        )
        await query.edit_message_caption(
            caption=success_msg,
            parse_mode='Markdown'
        )
        
        await generate_and_send_cv(query, context)
        
        return ConversationHandler.END
    else:
        keyboard = [
            [InlineKeyboardButton(
                "🔄 Check Again" if lang == "en" else "🔄 ពិនិត្យម្តងទៀត",
                callback_data="verify_payment"
            )],
            [InlineKeyboardButton(
                "❌ Cancel" if lang == "en" else "❌ បោះបង់",
                callback_data="cancel_payment"
            )]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_caption(
            caption=get_text(lang, "payment_failed"),
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        
        return PAYMENT_VERIFICATION


async def cancel_payment_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    lang = context.user_data.get("language", "en")
    
    cleanup_images(context.user_data)
    
    await query.edit_message_caption(
        caption=get_text(lang, "cancel"),
        parse_mode='Markdown'
    )
    context.user_data.clear()
    return ConversationHandler.END


async def generate_and_send_cv(query, context):
    """Generate CV and send to user and admin with timeout handling"""
    lang = context.user_data.get("language", "en")
    
    try:
        await context.bot.send_message(
            chat_id=query.from_user.id,
            text=get_text(lang, "processing"),
            parse_mode='Markdown'
        )
        
        html_path = create_cv_html(context.user_data, lang)
        
        file_size_mb = os.path.getsize(html_path) / (1024 * 1024)
        print(f"✓ CV file size: {file_size_mb:.2f} MB")
        
        # Send to user with retry logic
        max_retries = 3
        retry_count = 0
        sent_to_user = False
        
        while retry_count < max_retries and not sent_to_user:
            try:
                with open(html_path, 'rb') as html_file:
                    await context.bot.send_document(
                        chat_id=query.from_user.id,
                        document=html_file,
                        filename=os.path.basename(html_path),
                        caption=get_text(lang, "success"),
                        parse_mode='Markdown',
                        read_timeout=60,
                        write_timeout=60,
                        connect_timeout=60,
                        pool_timeout=60
                    )
                sent_to_user = True
                print("✓ CV sent to user successfully")
            except Exception as e:
                retry_count += 1
                print(f"⚠️ User send attempt {retry_count} failed: {e}")
                if retry_count < max_retries:
                    await asyncio.sleep(2)
                else:
                    raise
        
        # Send to admin
        payment_data = context.user_data.get("payment")
        cv_type_label = "🎰 CASINO CV" if context.user_data['cv_type'] == 'casino' else "📄 NORMAL CV"
        
        amount_display = f"{payment_data['amount']:,}" if payment_data['currency'] == "KHR" else f"${payment_data['amount']}"
        
        admin_message = f"""
{cv_type_label}

📋 *New PAID CV Submission*

👤 *Name:* {context.user_data['name']}
📞 *Phone:* {context.user_data['phone']}
"""
        if context.user_data['cv_type'] == 'casino':
            admin_message += f"💼 *Position:* {context.user_data.get('position', 'N/A')}\n"
            admin_message += f"🎮 *Games:* {context.user_data.get('game', 'N/A')}\n"
        
        admin_message += f"""
💰 *Payment:* {amount_display} {payment_data['currency']}
📋 *Bill:* {payment_data['bill_number']}
📅 *Submitted:* {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
🆔 *User ID:* {query.from_user.id}
👥 *Username:* @{query.from_user.username if query.from_user.username else 'N/A'}
📊 *File Size:* {file_size_mb:.2f} MB

💡 Open the HTML file in a browser to print!
"""
        
        retry_count = 0
        sent_to_admin = False
        
        while retry_count < max_retries and not sent_to_admin:
            try:
                with open(html_path, 'rb') as html_file:
                    await context.bot.send_document(
                        chat_id=ADMIN_ID,
                        document=html_file,
                        filename=os.path.basename(html_path),
                        caption=admin_message,
                        parse_mode='Markdown',
                        read_timeout=60,
                        write_timeout=60,
                        connect_timeout=60,
                        pool_timeout=60
                    )
                sent_to_admin = True
                print("✓ CV sent to admin successfully")
            except Exception as e:
                retry_count += 1
                print(f"⚠️ Admin send attempt {retry_count} failed: {e}")
                if retry_count < max_retries:
                    await asyncio.sleep(2)
                else:
                    print(f"❌ Failed to send to admin after {max_retries} attempts")
        
        cleanup_images(context.user_data)
        
    except Exception as e:
        error_msg = "❌ Error creating CV. Please try again or contact support."
        if lang == "km":
            error_msg = "❌ មានបញ្ហាក្នុងការបង្កើត CV។ សូមព្យាយាមម្តងទៀត។"
        
        await context.bot.send_message(
            chat_id=query.from_user.id,
            text=error_msg
        )
        print(f"❌ Full error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        context.user_data.clear()


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = context.user_data.get("language", "en")
    
    cleanup_images(context.user_data)
    
    await update.message.reply_text(
        get_text(lang, "cancel"),
        reply_markup=ReplyKeyboardRemove(),
        parse_mode='Markdown'
    )
    context.user_data.clear()
    return ConversationHandler.END


async def main():
    TOKEN = "8240802425:AAHqsMTTFfQmIYtOBxb6wGV3xIhwF8N_2lU"
    
    # Configure timeouts
    from telegram.request import HTTPXRequest
    
    request = HTTPXRequest(
        connection_pool_size=8,
        read_timeout=60.0,
        write_timeout=60.0,
        connect_timeout=60.0,
        pool_timeout=60.0,
    )
    
    application = (
        Application.builder()
        .token(TOKEN)
        .request(request)
        .build()
    )
    
    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            LANGUAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, language)],
            CV_TYPE: [MessageHandler(filters.TEXT & ~filters.COMMAND, cv_type)],
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, name)],
            ADDRESS: [MessageHandler(filters.TEXT & ~filters.COMMAND, address)],
            PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, phone)],
            POSITION: [MessageHandler(filters.TEXT & ~filters.COMMAND, position)],
            NATIONALITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, nationality)],
            SEX: [MessageHandler(filters.TEXT & ~filters.COMMAND, sex)],
            MARITAL: [MessageHandler(filters.TEXT & ~filters.COMMAND, marital)],
            HEIGHT: [MessageHandler(filters.TEXT & ~filters.COMMAND, height)],
            WEIGHT: [MessageHandler(filters.TEXT & ~filters.COMMAND, weight)],
            DOB: [MessageHandler(filters.TEXT & ~filters.COMMAND, dob)],
            POB: [MessageHandler(filters.TEXT & ~filters.COMMAND, pob)],
            PHOTO: [MessageHandler((filters.PHOTO | filters.Document.IMAGE | filters.TEXT) & ~filters.COMMAND, photo)],
            ID_CARD_FRONT: [MessageHandler((filters.PHOTO | filters.Document.IMAGE | filters.TEXT) & ~filters.COMMAND, id_card_front)],
            ID_CARD_BACK: [MessageHandler((filters.PHOTO | filters.Document.IMAGE) & ~filters.COMMAND, id_card_back)],
            GAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, game)],
            EXPERIENCE: [MessageHandler(filters.TEXT & ~filters.COMMAND, experience)],
            EDUCATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, education)],
            LANGUAGES: [MessageHandler(filters.TEXT & ~filters.COMMAND, languages)],
            PAYMENT_CURRENCY: [MessageHandler(filters.TEXT & ~filters.COMMAND, payment_currency)],
            PAYMENT_VERIFICATION: [
                CallbackQueryHandler(verify_payment_callback, pattern="^verify_payment$"),
                CallbackQueryHandler(cancel_payment_callback, pattern="^cancel_payment$"),
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    
    application.add_handler(conv)
    
    print("=" * 80)
    print("🎨 Professional CV Generator Bot with Bakong Payment!")
    print("=" * 80)
    print("📋 Features:")
    print("  ✓ Bakong KHQR payment integration")
    print("  ✓ Automatic payment verification")
    print("  ✓ Image compression (300KB per image)")
    print("  ✓ Support for KHR and USD")
    print("  ✓ Beautiful Tailwind CSS design")
    print("  ✓ Bilingual (English & Khmer)")
    print("  ✓ Casino & Normal CV types")
    print("  ✓ 60-second timeouts with retry logic")
    print("  ✓ Auto image cleanup")
    print("=" * 80)
    print(f"💰 Pricing:")
    print(f"  Normal CV: {CV_PRICES['normal']['KHR']:,} KHR / ${CV_PRICES['normal']['USD']}")
    print(f"  Casino CV: {CV_PRICES['casino']['KHR']:,} KHR / ${CV_PRICES['casino']['USD']}")
    print("=" * 80)
    
    await application.initialize()
    await application.start()
    await application.updater.start_polling()
    
    try:
        await asyncio.Event().wait()
    except KeyboardInterrupt:
        await application.updater.stop()
        await application.stop()
        await application.shutdown()

if __name__ == "__main__":
    asyncio.run(main())