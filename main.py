import os, re, sqlite3, logging, secrets
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime, timezone
from telegram import Update, InlineKeyboardButton as B, InlineKeyboardMarkup as K
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters

TOKEN=os.environ["TELEGRAM_BOT_TOKEN"]
ADMIN_RAW=os.environ["ADMIN_TELEGRAM_ID"]
if not ADMIN_RAW.isdigit(): raise RuntimeError("ADMIN_TELEGRAM_ID must be numeric")
ADMIN=int(ADMIN_RAW); SUPPORT=os.getenv("SUPPORT_CONTACT","@os3ma")
DB=os.getenv("DATABASE_PATH","nexus_stars.sqlite3")
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
def now(): return datetime.now(timezone.utc).isoformat(timespec="seconds")
def conn():
 c=sqlite3.connect(DB,timeout=20); c.row_factory=sqlite3.Row; return c
def init():
 with conn() as c:
  c.execute("CREATE TABLE IF NOT EXISTS users(uid INTEGER PRIMARY KEY, name TEXT, username TEXT, lang TEXT DEFAULT 'ar', address TEXT, updated TEXT)")
  c.execute("""CREATE TABLE IF NOT EXISTS orders(oid TEXT PRIMARY KEY, uid INTEGER, qty INTEGER, amount TEXT, address TEXT, status TEXT, created TEXT, updated TEXT, stars_verified TEXT, paid TEXT, admin INTEGER)""")
  c.execute("""CREATE TABLE IF NOT EXISTS receipts(receipt_id TEXT PRIMARY KEY, oid TEXT UNIQUE, qty INTEGER, verified TEXT)""")
def user(u):
 with conn() as c:
  c.execute("""INSERT INTO users(uid,name,username,lang,updated) VALUES(?,?,?,'ar',?)
   ON CONFLICT(uid) DO UPDATE SET name=excluded.name,username=excluded.username,updated=excluded.updated""",(u.id,u.first_name or "",u.username or "",now()))
  return dict(c.execute("SELECT * FROM users WHERE uid=?",(u.id,)).fetchone())
def lang(uid):
 with conn() as c:
  r=c.execute("SELECT lang FROM users WHERE uid=?",(uid,)).fetchone()
 return r["lang"] if r else "ar"
def tr(l,k,**kw): return T.get(l,T["ar"])[k].format(**kw)
def price(q):
 x=Decimal(q)*Decimal("0.011")
 if q<50: x*=Decimal("0.95")
 return x.quantize(Decimal(".01"),rounding=ROUND_HALF_UP)
def valid(a): return bool(re.fullmatch(r"0x[0-9a-fA-F]{40}",a))
NAME="𝐍 𝐄 𝐗 𝐔 𝐒　𝐒 𝐓 𝐀 𝐑 𝐒"
T={
"ar":{"welcome":"مرحباً بك {name} 👋\n\nفـي ⭐ "+NAME,"sell":"بيع نجوم ⭐","support":"الدعم الفني 💬","language":"اللغة 🌐","back":"رجوع 🔙","ar":"🇸🇩 العربية","en":"🇬🇧 English","qty":"• الـحـد الأدنـى: 10 ⭐\n\n• كـم نـجـمـة تـريد بيـعـها ؟","qtyerr":"أدخل عدداً صحيحاً لا يقل عن 10 نجوم.","summary":"الـكـمـية: {q} ⭐\n\n• الـمبلـغ الـمـتوقـع: {amount} USDT\n\nاخـتار طـريـقة الإسـتلام:","bnb":"BNB (BEP20)","addr":"أدخل عنوان USDT على شبكة BNB (BEP20) الخاص بك\n\n⚠️ تأكد من صحة العنوان والشبكة. أي خطأ قد يؤدي إلى فقدان المبلغ. يمكنك إرسال عنوان جديد لتغييره.","addrerr":"تنسيق العنوان غير صحيح. يجب أن يبدأ بـ 0x ويتبعه 40 رمزاً سداسيّاً عشرياً.","review":"راجع طلبك:\nرقم الطلب: {oid}\nالكمية: {q} ⭐\nالمبلغ المتوقع: {amount} USDT\nالشبكة: BNB (BEP20)\nالعنوان: {address}\n\nالحالة: بانتظار التحقق من استلام النجوم. تأكيد الطلب لا ينقل النجوم تلقائياً.","confirm":"تأكيد الطلب ✅","cancel":"إلغاء ✖️","created":"تم تسجيل طلبك رقم {oid}. الحالة: بانتظار التحقق من استلام النجوم.","cancelled":"تم إلغاء العملية.","supporttext":"الدعم الفني: {contact}","verify":"⭐ تم التحقق من استلام النجوم","paidbtn":"💸 تم الدفع بنجاح","paid":"✅ تم الدفع بنجاح، شكراً لتعاملك مع Nexus ⭐","admin":"طلب جديد #{oid}\nالعميل: {name}\nالمستخدم: @{username}\nUser ID: {uid}\nالكمية: {q} ⭐\nالمبلغ: {amount} USDT\nالعنوان: {address}\nالحالة: بانتظار التحقق من استلام النجوم\nالوقت: {time}","adminonly":"هذا الأمر للمشرف فقط.","total":"إجمالي النجوم المسجلة كنجوم مستلمة فعلياً: {n} ⭐\nهذا مجموع سجلات البوت وليس رصيد تيليجرام المباشر.","error":"تعذر تنفيذ الإجراء."},
"en":{"welcome":"Welcome {name} 👋\n\nTo ⭐ "+NAME,"sell":"Sell Stars ⭐","support":"Support 💬","language":"Language 🌐","back":"Back 🔙","ar":"🇸🇩 العربية","en":"🇬🇧 English","qty":"• Minimum amount: 10 ⭐\n\n• How many Stars do you want to sell?","qtyerr":"Enter a whole number of at least 10 Stars.","summary":"Quantity: {q} ⭐\n\n• Expected amount: {amount} USDT\n\nChoose a receiving method:","bnb":"BNB (BEP20)","addr":"Enter your USDT receiving address on BNB Smart Chain (BEP20).\n\n⚠️ Verify the address and network carefully. Mistakes may cause loss of funds. Send a new address to change it.","addrerr":"Invalid format. The address must start with 0x followed by exactly 40 hexadecimal characters.","review":"Review your order:\nOrder ID: {oid}\nQuantity: {q} ⭐\nExpected amount: {amount} USDT\nNetwork: BNB (BEP20)\nAddress: {address}\n\nStatus: Awaiting verification that Stars were received. Confirming this order does not transfer Stars automatically.","confirm":"Confirm Order ✅","cancel":"Cancel ✖️","created":"Your order #{oid} has been recorded. Status: awaiting verification that Stars were received.","cancelled":"The process has been cancelled.","supporttext":"Support: {contact}","verify":"⭐ Mark Stars as received","paidbtn":"💸 Payment sent","paid":"✅ Payment sent successfully. Thank you for choosing Nexus ⭐","admin":"New order #{oid}\nCustomer: {name}\nUsername: @{username}\nUser ID: {uid}\nQuantity: {q} ⭐\nExpected payout: {amount} USDT\nAddress: {address}\nStatus: awaiting Stars receipt verification\nTime: {time}","adminonly":"Administrator only.","total":"Total Stars recorded as actually received: {n} ⭐\nThis is the bot's recorded total, not a live Telegram balance.","error":"Action failed."}}
def homekb(l): return K([[B(tr(l,"sell"),callback_data="sell")],[B(tr(l,"support"),callback_data="support")],[B(tr(l,"language"),callback_data="language")]])
def backkb(l,rows=None): return K((rows or [])+[[B(tr(l,"back"),callback_data="back")]])
async def interface(q,text,kb,parse_mode=None):
 try: await q.edit_message_text(text,reply_markup=kb,parse_mode=parse_mode)
 except Exception: logging.exception("Message edit failed")
async def start(u,c):
 c.user_data.clear(); d=user(u); l=d["lang"]
 m=await u.effective_message.reply_text(tr(l,"welcome",name=u.effective_user.first_name or "there"),reply_markup=homekb(l))
 c.user_data.update(step="home",mid=m.message_id)
async def callbacks(u,c):
 q=u.callback_query; await q.answer(); d=user(q.from_user); l=d["lang"]; uid=q.from_user.id
 c.user_data["mid"]=q.message.message_id
 a=q.data
 if a in ("sell","support","language"):
  c.user_data["step"]=a
  if a=="sell": await interface(q,tr(l,"qty"),backkb(l))
  elif a=="support": await interface(q,tr(l,"supporttext",contact=SUPPORT),backkb(l,[[B("Open support",url="https://t.me/"+SUPPORT.lstrip("@"))]]))
  else: await interface(q,tr(l,"language"),backkb(l,[[B(tr(l,"ar"),callback_data="lang:ar"),B(tr(l,"en"),callback_data="lang:en")]]))
 elif a.startswith("lang:"):
  nl=a.split(":")[1]
  with conn() as db: db.execute("UPDATE users SET lang=?,updated=? WHERE uid=?",(nl,now(),uid))
  c.user_data["step"]="home"; await interface(q,tr(nl,"welcome",name=q.from_user.first_name or "there"),homekb(nl))
 elif a=="back":
  c.user_data["step"]="home"; await interface(q,tr(l,"welcome",name=q.from_user.first_name or "there"),homekb(l))
 elif a=="method":
  c.user_data["step"]="address"; saved=d.get("address")
  txt=tr(l,"addr")+(("\n\nSaved address: "+saved) if saved else "")
  await interface(q,txt,backkb(l))
 elif a=="cancel":
  c.user_data.pop("draft",None); c.user_data["step"]="home"
  await interface(q,tr(l,"cancelled"),homekb(l))
 elif a=="confirm":
  o=c.user_data.get("draft")
  if not o: await interface(q,tr(l,"error"),homekb(l)); return
  oid=secrets.token_hex(4).upper(); t=now()
  with conn() as db: db.execute("INSERT INTO orders VALUES(?,?,?,?,?,?,?, ?,NULL,NULL,NULL)",(oid,uid,o["q"],o["amount"],o["address"],"pending_stars",t,t))
  c.user_data.pop("draft",None); c.user_data["step"]="home"
  await interface(q,tr(l,"created",oid=oid),homekb(l))
  ad=tr("en","admin",oid=oid,name=q.from_user.first_name or "N/A",username=q.from_user.username or "N/A",uid=uid,q=o["q"],amount=o["amount"],address=o["address"],time=t)
  await c.bot.send_message(ADMIN,ad,reply_markup=K([[B(tr("en","verify"),callback_data="admin:verify:"+oid)]]))
 elif a.startswith("admin:"):
  if uid!=ADMIN: await q.answer(tr(l,"adminonly"),show_alert=True); return
  _,act,oid=a.split(":",2)
  with conn() as db:
   o=db.execute("SELECT * FROM orders WHERE oid=?",(oid,)).fetchone()
   if not o: await q.answer("Order not found",show_alert=True); return
   if act=="verify" and o["status"]=="pending_stars":
    t=now(); db.execute("UPDATE orders SET status='stars_verified',stars_verified=?,updated=?,admin=? WHERE oid=?",(t,t,ADMIN,oid))
    db.execute("INSERT OR IGNORE INTO receipts VALUES(?,?,?,?)",("manual-"+oid,oid,o["qty"],t))
    await q.edit_message_reply_markup(reply_markup=K([[B(tr("en","paidbtn"),callback_data="admin:paid:"+oid)]]))
   elif act=="paid" and o["status"]=="stars_verified":
    t=now(); db.execute("UPDATE orders SET status='paid',paid=?,updated=?,admin=? WHERE oid=?",(t,t,ADMIN,oid))
    try: await c.bot.send_message(o["uid"],tr(lang(o["uid"]),"paid"))
    except Exception: logging.exception("Customer notification failed")
    await q.edit_message_reply_markup(reply_markup=None)
   else: await q.answer(tr("en","error"),show_alert=True)
async def texts(u,c):
 m=u.effective_message; uid=u.effective_user.id; d=user(u.effective_user); l=d["lang"]; step=c.user_data.get("step","home")
 if not m or not m.text: return
 s=m.text.strip()
 try: await m.delete()
 except Exception: pass
 mid=c.user_data.get("mid")
 if step=="sell":
  if not s.isascii() or not s.isdigit() or int(s)<10:
   try: await c.bot.edit_message_text(chat_id=uid,message_id=mid,text=tr(l,"qtyerr"),reply_markup=backkb(l))
   except Exception: pass
   return
  q=int(s); amount=price(q); c.user_data.update(q=q,amount=str(amount),step="summary")
  await c.bot.edit_message_text(chat_id=uid,message_id=mid,text=tr(l,"summary",q=q,amount=f"{amount:.2f}"),reply_markup=backkb(l,[[B(tr(l,"bnb"),callback_data="method")]]))
 elif step=="address":
  if not valid(s):
   try: await c.bot.edit_message_text(chat_id=uid,message_id=mid,text=tr(l,"addrerr")+"\n\n"+tr(l,"addr"),reply_markup=backkb(l))
   except Exception: pass
   return
  with conn() as db: db.execute("UPDATE users SET address=?,updated=? WHERE uid=?",(s,now(),uid))
  if not c.user_data.get("q") or not c.user_data.get("amount"):
   c.user_data["step"]="sell"; await c.bot.edit_message_text(chat_id=uid,message_id=mid,text=tr(l,"qty"),reply_markup=backkb(l)); return
  c.user_data["draft"]={"q":c.user_data["q"],"amount":c.user_data["amount"],"address":s}; c.user_data["step"]="confirm"
  txt=tr(l,"review",oid="assigned after confirmation",q=c.user_data["q"],amount=c.user_data["amount"],address=s)
  await c.bot.edit_message_text(chat_id=uid,message_id=mid,text=txt,reply_markup=backkb(l,[[B(tr(l,"confirm"),callback_data="confirm"),B(tr(l,"cancel"),callback_data="cancel")]]))
async def total(u,c):
 user(u.effective_user); l=lang(u.effective_user.id)
 if u.effective_user.id!=ADMIN: await u.effective_message.reply_text(tr(l,"adminonly")); return
 with conn() as db: n=db.execute("SELECT COALESCE(SUM(qty),0) n FROM receipts").fetchone()["n"]
 await u.effective_message.reply_text(tr(l,"total",n=n))
async def err(u,c): logging.exception("Unhandled update error",exc_info=c.error)
def main():
 init(); app=Application.builder().token(TOKEN).build()
 app.add_handler(CommandHandler("start",start)); app.add_handler(CommandHandler("stars_total",total))
 app.add_handler(CallbackQueryHandler(callbacks)); app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND,texts)); app.add_error_handler(err)
 app.run_polling(allowed_updates=Update.ALL_TYPES)
if __name__=="__main__": main()
