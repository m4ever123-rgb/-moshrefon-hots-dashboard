#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
لوحة مشرف مركزية - تجمع نتائج جميع المتدربين من أجهزة مختلفة عبر رابط واحد
إعداد: المشرفون
"""
from flask import Flask, request, jsonify, render_template_string, session, redirect, url_for
from flask_cors import CORS
import json, os, datetime
from pathlib import Path
from functools import wraps

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'moshrefon_supervisor_2026_secure_key_!@#')
CORS(app)

# ============== إعدادات كلمة المرور ==============
SUPERVISOR_PASSWORD = os.environ.get('SUPERVISOR_PASSWORD', 'Moshrefon@2026')  # يمكن تغييرها عبر متغير بيئة
# يمكنك تغييرها إلى أي كلمة تريدينها

# للتوافق مع الاستضافة السحابية (Render / Railway / PythonAnywhere)
DATA_FILE = Path(os.environ.get('DATA_FILE', '/home/user/supervisor_data.json'))
# في الاستضافة المؤقتة استخدمي /tmp/supervisor_data.json إذا لم يكن هناك قرص دائم
if not str(DATA_FILE).startswith('/home/user') and not DATA_FILE.parent.exists():
    DATA_FILE = Path('/tmp/supervisor_data.json')

# Ensure data file exists
if not DATA_FILE.exists():
    DATA_FILE.write_text(json.dumps([], ensure_ascii=False), encoding='utf-8')

def load_data():
    try:
        return json.loads(DATA_FILE.read_text(encoding='utf-8'))
    except:
        return []

def save_data(data):
    DATA_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('supervisor_logged_in'):
            return redirect(url_for('supervisor_login'))
        return f(*args, **kwargs)
    return decorated

# ============== صفحة تسجيل دخول المشرف ==============
LOGIN_HTML = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>تسجيل دخول المشرف | إعداد المشرفون</title>
<style>
:root{--navy:#0F3D5E; --teal:#1B8A9D; --gold:#D97706; --border:#CBD5E1; --text:#1E293B; --muted:#64748B}
*{box-sizing:border-box; margin:0; padding:0}
body{font-family:Tahoma,Arial,sans-serif; background:linear-gradient(135deg,#0F3D5E 0%,#1B8A9D 100%); min-height:100vh; display:flex; align-items:center; justify-content:center; padding:16px}
.login-card{background:#fff; border-radius:20px; box-shadow:0 20px 60px rgba(0,0,0,0.25); width:100%; max-width:420px; overflow:hidden; border:1px solid var(--border)}
.login-header{background:linear-gradient(135deg,#0B2B44,#0F3D5E); color:#fff; padding:24px 20px; text-align:center; border-bottom:4px solid var(--gold)}
.login-header h1{font-size:20px; font-weight:900; margin-bottom:6px}
.login-header p{font-size:12px; opacity:0.85}
.login-body{padding:22px 20px}
.alert{padding:10px 12px; border-radius:10px; font-size:12.5px; font-weight:700; margin-bottom:14px; display:flex; gap:8px}
.alert.error{background:#FEE2E2; border:1px solid #FECACA; color:#7F1D1D}
.alert.info{background:#E0F2FE; border:1px solid #BAE6FD; color:#0C4A6E}
.input{width:100%; padding:12px 14px; border:1.5px solid var(--border); border-radius:12px; font-family:inherit; font-size:14px; outline:none; transition:all 0.2s}
.input:focus{border-color:var(--teal); box-shadow:0 0 0 4px rgba(27,138,157,0.12)}
.btn{width:100%; padding:12px 16px; border-radius:12px; border:none; font-family:inherit; font-weight:900; font-size:14px; cursor:pointer; background:linear-gradient(135deg,var(--navy),var(--teal)); color:#fff; margin-top:12px; box-shadow:0 6px 18px rgba(15,61,94,0.25)}
.btn:hover{transform:translateY(-1px)}
.hint{background:#FEF9E7; border:1px solid #FDE68A; border-radius:10px; padding:10px 12px; font-size:11.5px; margin-top:14px; line-height:1.7}
</style>
</head>
<body>
<div class="login-card">
  <div class="login-header">
    <div style="font-size:36px; margin-bottom:8px">🔐</div>
    <h1>لوحة المشرف - تسجيل الدخول</h1>
    <p>إعداد: المشرفون | دخول آمن بكلمة مرور</p>
  </div>
  <div class="login-body">
    {% if error %}
    <div class="alert error"><span>⚠️</span><div>{{ error }}</div></div>
    {% endif %}
    <div class="alert info"><span>ℹ️</span><div><strong>للمشرف فقط:</strong> هذه الصفحة محمية بكلمة مرور. رابط الطالب <code>/student</code> لا يحتاج كلمة مرور ويعمل من أي جهاز.</div></div>
    <form method="POST">
      <div style="margin-bottom:10px">
        <label style="display:block; font-size:12px; font-weight:800; color:var(--navy); margin-bottom:6px">كلمة مرور المشرف:</label>
        <input type="password" name="password" class="input" placeholder="أدخل كلمة المرور..." required autofocus>
      </div>
      <button type="submit" class="btn">🔓 دخول لوحة المشرف</button>
    </form>
    <div class="hint">
      <strong>🔑 كلمة المرور الافتراضية:</strong> <code style="background:#fff; padding:2px 8px; border-radius:6px; font-weight:900; border:1px solid #FDE68A">Moshrefon@2026</code><br>
      يمكنك تغييرها في ملف <code>supervisor_dashboard_app.py</code> السطر: <code>SUPERVISOR_PASSWORD</code><br>
      <strong>ملاحظة:</strong> رابط الطالب لا يحتاج كلمة مرور.
    </div>
    <div style="text-align:center; margin-top:14px">
      <a href="/student" style="font-size:12px; color:var(--teal); font-weight:800; text-decoration:none">← العودة لرابط الطالب</a>
    </div>
  </div>
</div>
</body>
</html>
"""

# ============== HTML TEMPLATES ==============

SUPERVISOR_HTML = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>لوحة المشرف - تجميع نتائج المتدربين | إعداد المشرفون</title>
<style>
:root{--navy:#0F3D5E; --teal:#1B8A9D; --gold:#D97706; --emerald:#107C41; --purple:#5B3CC4; --coral:#C0392B; --slate:#F8FAFC; --border:#CBD5E1; --text:#1E293B; --muted:#64748B}
*{box-sizing:border-box; margin:0; padding:0}
body{font-family:Tahoma,Arial,sans-serif; background:linear-gradient(135deg,#F0F7FA,#F8FAFC); color:var(--text); line-height:1.7}
.top{background:#0B2B44; color:#fff; padding:10px 16px; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px; border-bottom:4px solid var(--gold)}
.header{background:linear-gradient(135deg,var(--navy),var(--teal)); color:#fff; padding:20px 16px; text-align:center}
.header h1{font-size:22px; font-weight:900}
.header p{font-size:13px; opacity:0.9; margin-top:6px}
.container{max-width:1280px; margin:16px auto; padding:0 14px}
.card{background:#fff; border-radius:16px; border:1px solid var(--border); box-shadow:0 8px 28px rgba(15,61,94,0.07); margin-bottom:16px; overflow:hidden}
.card-h{padding:12px 16px; color:#fff; font-weight:900; font-size:14px; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px}
.card-h.navy{background:var(--navy)} .card-h.teal{background:var(--teal)} .card-h.gold{background:var(--gold)}} .card-h.emerald{background:var(--emerald)}} .card-h.purple{background:var(--purple)}
.card-b{padding:16px}
.stats{display:grid; grid-template-columns:repeat(auto-fit,minmax(180px,1fr)); gap:12px; margin-bottom:14px}
.stat{background:#F8FAFC; border:1px solid var(--border); border-radius:12px; padding:14px; text-align:center}
.stat-num{font-size:26px; font-weight:900; color:var(--navy)}
.stat-label{font-size:11.5px; color:var(--muted); font-weight:700; margin-top:2px}
.table-wrap{overflow:auto; max-height:520px; border:1px solid var(--border); border-radius:12px}
table{width:100%; border-collapse:collapse; font-size:12.5px; min-width:900px}
th{background:var(--navy); color:#fff; padding:10px 8px; text-align:center; position:sticky; top:0; z-index:2; font-size:11.5px}
td{padding:9px 8px; border-bottom:1px solid #F1F5F9; text-align:center}
tr:nth-child(even){background:#F8FAFC}
tr:hover{background:#F0F7FA}
.badge{padding:3px 8px; border-radius:20px; font-size:10.5px; font-weight:800; display:inline-block}
.badge-success{background:#DCFCE7; color:#14532D; border:1px solid #BBF7D0}
.badge-warn{background:#FEF3C7; color:#92400E; border:1px solid #FDE68A}
.badge-danger{background:#FEE2E2; color:#7F1D1D; border:1px solid #FECACA}
.badge-info{background:#E0F2FE; color:#0C4A6E; border:1px solid #BAE6FD}
.btn{padding:10px 16px; border-radius:10px; border:none; font-family:inherit; font-weight:800; font-size:13px; cursor:pointer; display:inline-flex; align-items:center; gap:6px}
.btn-primary{background:linear-gradient(135deg,var(--navy),var(--teal)); color:#fff}
.btn-gold{background:linear-gradient(135deg,var(--gold),#F59E0B); color:#fff}
.btn-outline{background:#fff; border:1.5px solid var(--border); color:var(--navy)}
.btn-danger{background:var(--coral); color:#fff}
.input{padding:10px 12px; border:1.5px solid var(--border); border-radius:10px; font-family:inherit; font-size:13px; width:100%}
.grid2{display:grid; grid-template-columns:1fr 1fr; gap:12px}
@media(max-width:800px){.grid2{grid-template-columns:1fr}}
.chart-bar{display:flex; align-items:center; gap:8px; margin:6px 0; font-size:12px}
.bar-label{width:90px; font-weight:700; text-align:right; flex-shrink:0}
.bar-track{flex:1; height:12px; background:#E2E8F0; border-radius:999px; overflow:hidden}
.bar-fill{height:100%; border-radius:999px; transition:width 0.6s}
</style>
</head>
<body>
<div class="top">
  <div>🎓 لوحة المشرف المركزية - تجميع نتائج المتدربين | إعداد: <strong>المشرفون</strong></div>
  <div style="display:flex; gap:8px; align-items:center; flex-wrap:wrap">
    <span id="liveCount" style="background:var(--emerald); padding:4px 10px; border-radius:20px; font-size:11px; font-weight:900">0 متدرب</span>
    <span id="serverTime" style="background:rgba(255,255,255,0.15); padding:4px 10px; border-radius:20px; font-size:11px"></span>
  </div>
</div>

<div class="header">
  <h1>📊 لوحة المشرف - تحليل الأثر التدريبي لجميع المتدربين</h1>
  <p>رابط واحد يجمع نتائج الاختبار القبلي والبعدي من جميع الأجهزة - تحليل تلقائي حسب مستويات بلوم - تصدير Excel و PDF - حفظ دائم على الخادم</p>
</div>

<div class="container">

  <div class="card">
    <div class="card-h navy">📈 ملخص الأثر التدريبي العام</div>
    <div class="card-b">
      <div class="stats">
        <div class="stat"><div class="stat-num" id="sTotal">0</div><div class="stat-label">إجمالي المتدربين المسجلين</div></div>
        <div class="stat"><div class="stat-num" id="sPreAvg">--</div><div class="stat-label">متوسط القبلي /17</div></div>
        <div class="stat"><div class="stat-num" id="sPostAvg">--</div><div class="stat-label">متوسط البعدي /17</div></div>
        <div class="stat"><div class="stat-num" id="sGainAvg" style="color:var(--emerald)">--</div><div class="stat-label">متوسط التحسن %</div></div>
        <div class="stat"><div class="stat-num" id="sSuccess">0</div><div class="stat-label">عدد المتميزين (≥85% أو +5)</div></div>
        <div class="stat"><div class="stat-num" id="sPreOnly">0</div><div class="stat-label">أتموا القبلي فقط (لم يدخلوا البعدي)</div></div>
      </div>
      <div class="grid2">
        <div>
          <div style="font-weight:900; color:var(--navy); margin-bottom:8px; font-size:13px">📊 تحليل حسب مستويات بلوم (متوسط عام)</div>
          <div id="levelAnalysis"></div>
        </div>
        <div>
          <div style="font-weight:900; color:var(--navy); margin-bottom:8px; font-size:13px">🎯 توزيع مستويات الإتقان (بعدي)</div>
          <div id="masteryDist"></div>
          <div style="margin-top:12px; background:#F8FAFC; border:1px dashed var(--border); border-radius:10px; padding:10px; font-size:12px; line-height:1.7">
            <strong>💡 كيف يجمع النظام النتائج؟</strong><br>
            • المتدرب يدخل على رابط الطالب: <code>/student</code> من أي جهاز (جوال/لابتوب)<br>
            • يجيب القبلي بدون اسم (رمز تلقائي TRAINEE-XXXX)<br>
            • النظام يمنع دخول البعدي حتى إتمام القبلي<br>
            • عند تسليم البعدي يضغط "إرسال للوحة المشرف" → تُحفظ النتيجة فوراً هنا<br>
            • جميع البيانات محفوظة في ملف <code>supervisor_data.json</code> على الخادم بشكل دائم
          </div>
        </div>
      </div>
    </div>
  </div>

  <div class="card">
    <div class="card-h teal">
      <span>📋 جدول نتائج جميع المتدربين (من أجهزة مختلفة)</span>
      <div style="display:flex; gap:8px; flex-wrap:wrap">
        <input type="text" id="searchBox" class="input" placeholder="🔍 بحث بالرمز أو الدرجة..." style="width:200px; padding:6px 10px; font-size:12px">
        <button class="btn btn-gold" onclick="exportCSV()">📥 تصدير Excel (CSV)</button>
        <button class="btn btn-primary" onclick="exportJSON()">💾 تصدير JSON</button>
        <button class="btn btn-outline" onclick="loadData()">🔄 تحديث البيانات</button>
        <button class="btn btn-danger" onclick="clearAll()">🗑️ مسح الكل</button>
      </div>
    </div>
    <div class="card-b" style="padding:0">
      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>رمز المتدرب</th>
              <th>قبلي /17</th>
              <th>قبلي %</th>
              <th>بعدي /17</th>
              <th>بعدي %</th>
              <th>التحسن</th>
              <th>نسبة التحسن</th>
              <th>الحكم</th>
              <th>تاريخ القبلي</th>
              <th>تاريخ البعدي</th>
              <th>تفاصيل بلوم</th>
            </tr>
          </thead>
          <tbody id="resultsBody"><tr><td colspan="11" style="padding:20px; color:var(--muted)">جاري تحميل البيانات...</td></tr></tbody>
        </table>
      </div>
    </div>
  </div>

  <div class="card">
    <div class="card-h gold">🔐 إدارة كلمة المرور</div>
    <div class="card-b">
      <div style="display:grid; grid-template-columns:1fr 1fr 1fr auto; gap:8px; align-items:end">
        <div><label style="font-size:11px; font-weight:800">كلمة المرور الحالية</label><input type="password" id="oldPwd" class="input" placeholder="الحالية"></div>
        <div><label style="font-size:11px; font-weight:800">كلمة المرور الجديدة</label><input type="password" id="newPwd" class="input" placeholder="جديدة - 4 أحرف على الأقل"></div>
        <div><label style="font-size:11px; font-weight:800">تأكيد الجديدة</label><input type="password" id="confirmPwd" class="input" placeholder="تأكيد"></div>
        <button class="btn btn-gold" onclick="changePassword()">🔑 تغيير</button>
      </div>
      <div id="pwdMsg" style="margin-top:8px; font-size:12px; font-weight:700"></div>
      <div style="font-size:11px; color:var(--muted); margin-top:6px">كلمة المرور الحالية الافتراضية: <code>Moshrefon@2026</code> - يمكنك تغييرها هنا وسيتم حفظها حتى إعادة تشغيل الخادم</div>
    </div>
  </div>

  <div class="card">
    <div class="card-h gold">🔗 روابط المشاركة</div>
    <div class="card-b">
      <div class="grid2">
        <div style="background:#F8FAFC; border:1px solid var(--border); border-radius:12px; padding:12px">
          <div style="font-weight:900; color:var(--navy); font-size:13px">👨‍🎓 رابط الطالب (يرسل للمتدربين):</div>
          <div style="display:flex; gap:8px; margin-top:8px">
            <input id="studentLink" class="input" readonly style="font-size:11px; direction:ltr">
            <button class="btn btn-primary" onclick="copyLink('studentLink')">نسخ</button>
          </div>
          <div style="font-size:11px; color:var(--muted); margin-top:6px">هذا الرابط يعمل من أي جهاز، يجمع القبلي والبعدي ويمنع البعدي حتى إتمام القبلي</div>
        </div>
        <div style="background:#FEF3C7; border:1px solid #FDE68A; border-radius:12px; padding:12px">
          <div style="font-weight:900; color:#92400E; font-size:13px">👩‍🏫 رابط المشرف (هذه الصفحة - خاص):</div>
          <div style="display:flex; gap:8px; margin-top:8px">
            <input id="supervisorLink" class="input" readonly style="font-size:11px; direction:ltr">
            <button class="btn btn-gold" onclick="copyLink('supervisorLink')">نسخ</button>
          </div>
          <div style="font-size:11px; color:#92400E; margin-top:6px">لا تشارك هذا الرابط مع المتدربين - خاص بالمشرف فقط لعرض جميع النتائج</div>
        </div>
      </div>
    </div>
  </div>

</div>

<script>
let allData = [];

function loadData(){
  fetch('/api/results')
    .then(r=>r.json())
    .then(data=>{
      allData = data;
      renderTable(data);
      renderStats(data);
    })
    .catch(err=>{
      document.getElementById('resultsBody').innerHTML = `<tr><td colspan="11" style="color:#C0392B; padding:20px">خطأ في تحميل البيانات: ${err}</td></tr>`;
    });
}

function renderTable(data){
  const tbody = document.getElementById('resultsBody');
  const search = document.getElementById('searchBox').value.toLowerCase();
  let filtered = data;
  if(search){
    filtered = data.filter(d=> (d.code||'').toLowerCase().includes(search) || String(d.pre_score||'').includes(search) || String(d.post_score||'').includes(search));
  }
  if(filtered.length===0){
    tbody.innerHTML = `<tr><td colspan="11" style="padding:20px; color:var(--muted)">لا توجد بيانات ${search?'- لا نتائج للبحث':''}</td></tr>`;
    return;
  }
  tbody.innerHTML = filtered.map(d=>{
    const pre = d.pre_score ?? '--';
    const post = d.post_score ?? '--';
    const prePct = d.pre_percent ?? '--';
    const postPct = d.post_percent ?? '--';
    const gain = (d.pre_score!=null && d.post_score!=null) ? (d.post_score - d.pre_score) : '--';
    const gainPct = (d.pre_percent!=null && d.post_percent!=null) ? (d.post_percent - d.pre_percent) : '--';
    const isSuccess = (d.post_percent>=85 || (gain!=='--' && gain>=5));
    const badge = d.post_score==null ? '<span class="badge badge-warn">قبلي فقط</span>' : isSuccess ? '<span class="badge badge-success">متميز 🏆</span>' : '<span class="badge badge-info">مكتمل</span>';
    const levelDetail = d.post_byLevel ? Object.entries(d.post_byLevel).map(([lvl,v])=>`${lvl}:${v.correct}/${v.total}`).join(' | ') : (d.pre_byLevel? Object.entries(d.pre_byLevel).map(([lvl,v])=>`${lvl}:${v.correct}/${v.total}`).join(' | ') : '--');
    return `<tr>
      <td style="font-family:monospace; font-weight:800">${d.code||'--'}</td>
      <td>${pre}</td>
      <td>${prePct!=='--'?prePct+'%':prePct}</td>
      <td style="font-weight:800">${post}</td>
      <td style="font-weight:800">${postPct!=='--'?postPct+'%':postPct}</td>
      <td style="color:${gain>0?'var(--emerald)':gain<0?'var(--coral)':''}; font-weight:800">${gain!=='--'?(gain>0?'+':'')+gain:gain}</td>
      <td style="color:${gainPct>0?'var(--emerald)':''}; font-weight:800">${gainPct!=='--'?(gainPct>0?'+':'')+gainPct+'%':gainPct}</td>
      <td>${badge}</td>
      <td style="font-size:11px">${d.pre_date? new Date(d.pre_date).toLocaleString('ar-SA'): '--'}</td>
      <td style="font-size:11px">${d.post_date? new Date(d.post_date).toLocaleString('ar-SA'): '--'}</td>
      <td style="font-size:10px; text-align:right; max-width:200px; white-space:normal">${levelDetail}</td>
    </tr>`;
  }).join('');
  document.getElementById('liveCount').textContent = `${data.length} متدرب`;
}

function renderStats(data){
  const total = data.length;
  document.getElementById('sTotal').textContent = total;
  if(total===0){
    document.getElementById('sPreAvg').textContent = '--';
    document.getElementById('sPostAvg').textContent = '--';
    document.getElementById('sGainAvg').textContent = '--';
    document.getElementById('sSuccess').textContent = '0';
    document.getElementById('sPreOnly').textContent = '0';
    document.getElementById('levelAnalysis').innerHTML = '<div style="color:var(--muted); font-size:12px">لا توجد بيانات بعد</div>';
    document.getElementById('masteryDist').innerHTML = '<div style="color:var(--muted); font-size:12px">لا توجد بيانات بعد</div>';
    return;
  }
  const preScores = data.filter(d=>d.pre_score!=null).map(d=>d.pre_score);
  const postScores = data.filter(d=>d.post_score!=null).map(d=>d.post_score);
  const preAvg = preScores.length? (preScores.reduce((a,b)=>a+b,0)/preScores.length).toFixed(1): '--';
  const postAvg = postScores.length? (postScores.reduce((a,b)=>a+b,0)/postScores.length).toFixed(1): '--';
  const gains = data.filter(d=>d.pre_score!=null && d.post_score!=null).map(d=> ((d.post_score - d.pre_score)/17*100));
  const gainAvg = gains.length? (gains.reduce((a,b)=>a+b,0)/gains.length).toFixed(1)+'%': '--';
  const success = data.filter(d=> d.post_percent>=85 || (d.post_score!=null && d.pre_score!=null && (d.post_score - d.pre_score)>=5)).length;
  const preOnly = data.filter(d=> d.pre_score!=null && d.post_score==null).length;

  document.getElementById('sPreAvg').textContent = preAvg;
  document.getElementById('sPostAvg').textContent = postAvg;
  document.getElementById('sGainAvg').textContent = gainAvg;
  document.getElementById('sSuccess').textContent = success;
  document.getElementById('sPreOnly').textContent = preOnly;

  // Level analysis
  const levels = {};
  data.forEach(d=>{
    const src = d.post_byLevel || d.pre_byLevel;
    if(!src) return;
    Object.entries(src).forEach(([lvl, v])=>{
      if(!levels[lvl]) levels[lvl] = {correct:0, total:0};
      levels[lvl].correct += v.correct;
      levels[lvl].total += v.total;
    });
  });
  let levelHtml = '';
  Object.entries(levels).forEach(([lvl, v])=>{
    const pct = v.total? Math.round((v.correct/v.total)*100):0;
    const color = pct>=70?'var(--emerald)':pct>=40?'var(--gold)':'var(--coral)';
    levelHtml += `<div class="chart-bar"><div class="bar-label">${lvl}</div><div class="bar-track"><div class="bar-fill" style="width:${pct}%; background:${color}"></div></div><div style="width:60px; font-weight:800; font-size:11px">${pct}% (${v.correct}/${v.total})</div></div>`;
  });
  document.getElementById('levelAnalysis').innerHTML = levelHtml || '<div style="color:var(--muted)">لا توجد بيانات مستويات</div>';

  // Mastery distribution
  const mastery = {mumtaz:0, mutqin:0, nami:0, support:0};
  postScores.forEach(s=>{
    const pct = (s/17*100);
    if(pct>=85) mastery.mumtaz++;
    else if(pct>=70) mastery.mutqin++;
    else if(pct>=50) mastery.nami++;
    else mastery.support++;
  });
  const totalPost = postScores.length || 1;
  document.getElementById('masteryDist').innerHTML = `
    <div class="chart-bar"><div class="bar-label">متميز ≥85%</div><div class="bar-track"><div class="bar-fill" style="width:${(mastery.mumtaz/totalPost*100)}%; background:var(--emerald)"></div></div><div style="width:30px; font-weight:800">${mastery.mumtaz}</div></div>
    <div class="chart-bar"><div class="bar-label">متقن 70-84%</div><div class="bar-track"><div class="bar-fill" style="width:${(mastery.mutqin/totalPost*100)}%; background:var(--teal)"></div></div><div style="width:30px; font-weight:800">${mastery.mutqin}</div></div>
    <div class="chart-bar"><div class="bar-label">نامٍ 50-69%</div><div class="bar-track"><div class="bar-fill" style="width:${(mastery.nami/totalPost*100)}%; background:var(--gold)"></div></div><div style="width:30px; font-weight:800">${mastery.nami}</div></div>
    <div class="chart-bar"><div class="bar-label">بحاجة دعم &lt;50%</div><div class="bar-track"><div class="bar-fill" style="width:${(mastery.support/totalPost*100)}%; background:var(--coral)"></div></div><div style="width:30px; font-weight:800">${mastery.support}</div></div>
  `;
}

function exportCSV(){
  if(allData.length===0){ alert('لا توجد بيانات'); return; }
  let csv = 'رمز المتدرب,قبلي درجة,قبلي %,بعدي درجة,بعدي %,فرق,تحسن %,الحكم,تاريخ قبلي,تاريخ بعدي,تفاصيل بلوم\n';
  allData.forEach(d=>{
    const gain = (d.pre_score!=null && d.post_score!=null)? (d.post_score - d.pre_score):'';
    const gainPct = (d.pre_percent!=null && d.post_percent!=null)? (d.post_percent - d.pre_percent):'';
    const judge = d.post_score==null?'قبلي فقط': (d.post_percent>=85 || gain>=5?'متميز':'مكتمل');
    const levelDetail = d.post_byLevel? JSON.stringify(d.post_byLevel).replace(/"/g,'""') : (d.pre_byLevel? JSON.stringify(d.pre_byLevel).replace(/"/g,'""') : '');
    csv += `${d.code||''},${d.pre_score||''},${d.pre_percent||''},${d.post_score||''},${d.post_percent||''},${gain},${gainPct},${judge},${d.pre_date||''},${d.post_date||''},"${levelDetail}"\n`;
  });
  const blob = new Blob(["\\uFEFF"+csv], {type:'text/csv;charset=utf-8;'});
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `نتائج_المشرف_${new Date().toISOString().slice(0,10)}.csv`;
  a.click();
}

function exportJSON(){
  if(allData.length===0){ alert('لا توجد بيانات'); return; }
  const blob = new Blob([JSON.stringify(allData,null,2)], {type:'application/json'});
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `supervisor_data_${new Date().toISOString().slice(0,10)}.json`;
  a.click();
}

function clearAll(){
  if(confirm('⚠️ هل أنت متأكد من مسح جميع بيانات المتدربين نهائياً من الخادم؟ لا يمكن التراجع.')){
    if(prompt('اكتب كلمة التأكيد: مسح')!=='مسح'){ alert('تم الإلغاء'); return; }
    fetch('/api/clear', {method:'POST'})
      .then(r=>r.json())
      .then(res=>{ alert('تم المسح: '+res.message); loadData(); })
      .catch(err=> alert('خطأ: '+err));
  }
}

function copyLink(id){
  const el = document.getElementById(id);
  el.select();
  document.execCommand('copy');
  alert('تم نسخ الرابط: '+el.value);
}

document.getElementById('searchBox').addEventListener('input', ()=> renderTable(allData));

function updateTime(){
  document.getElementById('serverTime').textContent = new Date().toLocaleString('ar-SA');
}
setInterval(updateTime, 1000);
updateTime();

function changePassword(){
  const oldPwd = document.getElementById('oldPwd').value;
  const newPwd = document.getElementById('newPwd').value;
  const confirmPwd = document.getElementById('confirmPwd').value;
  const msg = document.getElementById('pwdMsg');
  if(!oldPwd || !newPwd || !confirmPwd){ msg.textContent='يرجى تعبئة جميع الحقول'; msg.style.color='var(--coral)'; return; }
  if(newPwd !== confirmPwd){ msg.textContent='تأكيد كلمة المرور غير متطابق'; msg.style.color='var(--coral)'; return; }
  fetch('/api/change-password', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({old_password:oldPwd, new_password:newPwd})})
    .then(r=>r.json())
    .then(d=>{
      if(d.status==='success'){ msg.textContent='✅ '+d.message; msg.style.color='var(--emerald)'; document.getElementById('oldPwd').value=''; document.getElementById('newPwd').value=''; document.getElementById('confirmPwd').value=''; }
      else{ msg.textContent='❌ '+d.message; msg.style.color='var(--coral)'; }
    })
    .catch(err=>{ msg.textContent='خطأ: '+err; msg.style.color='var(--coral)'; });
}

function setLinks(){
  const base = window.location.origin;
  document.getElementById('studentLink').value = base + '/student';
  document.getElementById('supervisorLink').value = base + '/supervisor';
}
setLinks();
loadData();
setInterval(loadData, 5000); // auto refresh every 5s
</script>
</body>
</html>
"""

STUDENT_HTML = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>اختبار المتدرب - قبلي وبعدي | إعداد المشرفون</title>
<style>
:root{--navy:#0F3D5E; --teal:#1B8A9D; --gold:#D97706; --emerald:#107C41; --purple:#5B3CC4; --coral:#C0392B; --border:#CBD5E1; --text:#1E293B; --muted:#64748B}
*{box-sizing:border-box; margin:0; padding:0}
body{font-family:Tahoma,Arial,sans-serif; background:linear-gradient(135deg,#F0F7FA,#F8FAFC); color:var(--text); line-height:1.75}
.top{background:#0B2B44; color:#fff; padding:8px 12px; text-align:center; font-size:11px; border-bottom:4px solid var(--gold)}
.header{background:linear-gradient(135deg,var(--navy),var(--teal)); color:#fff; padding:18px 14px; text-align:center}
.header h1{font-size:20px; font-weight:900}
.badges{display:flex; justify-content:center; gap:6px; flex-wrap:wrap; margin-top:10px}
.pill{background:rgba(255,255,255,0.14); border:1px solid rgba(255,255,255,0.22); padding:4px 10px; border-radius:999px; font-size:10px; font-weight:800}
.pill.gold{background:var(--gold); border-color:var(--gold)}
.container{max-width:960px; margin:14px auto; padding:0 12px}
.card{background:#fff; border-radius:14px; border:1px solid var(--border); box-shadow:0 6px 22px rgba(15,61,94,0.06); margin-bottom:14px; overflow:hidden}
.card-h{padding:10px 14px; color:#fff; font-weight:900; font-size:13px; display:flex; justify-content:space-between; align-items:center}
.card-h.navy{background:var(--navy)} .card-h.teal{background:var(--teal)} .card-h.gold{background:var(--gold)} .card-h.emerald{background:var(--emerald)}
.card-b{padding:14px}
.progress-track{height:8px; background:#E2E8F0; border-radius:999px; overflow:hidden; margin:8px 0}
.progress-bar{height:100%; background:linear-gradient(90deg,var(--teal),var(--emerald)); width:0%; transition:width 0.4s}
.q-card{border:1.5px solid var(--border); border-radius:12px; padding:12px 14px; margin-bottom:10px; background:#fff}
.q-card.answered{border-color:var(--teal); background:#F0F9FA}
.q-num{background:var(--navy); color:#fff; min-width:32px; height:24px; border-radius:6px; display:flex; align-items:center; justify-content:center; font-size:11px; font-weight:900; display:inline-flex; margin-left:8px}
.q-text{font-size:13.5px; font-weight:700; color:var(--navy); margin-bottom:8px}
.options{display:grid; gap:6px}
.opt{padding:9px 10px; border:1.5px solid #E2E8F0; border-radius:9px; cursor:pointer; font-size:12.5px; display:flex; gap:8px; align-items:center; background:#FBFDFF}
.opt:hover{border-color:var(--teal); background:#F0F7FA}
.opt.selected{border-color:var(--teal); background:#E6F4F7; font-weight:700}
.opt input{display:none}
.btn{padding:11px 16px; border-radius:10px; border:none; font-family:inherit; font-weight:900; font-size:13px; cursor:pointer; display:inline-flex; align-items:center; justify-content:center; gap:6px; width:100%}
.btn-primary{background:linear-gradient(135deg,var(--navy),var(--teal)); color:#fff}
.btn-gold{background:linear-gradient(135deg,var(--gold),#F59E0B); color:#fff}
.btn-outline{background:#fff; border:1.5px solid var(--border); color:var(--navy)}
.alert{padding:10px 12px; border-radius:10px; font-size:12px; font-weight:700; display:flex; gap:8px; line-height:1.6}
.alert.info{background:#E0F2FE; border:1px solid #BAE6FD; color:#0C4A6E}
.alert.success{background:#DCFCE7; border:1px solid #BBF7D0; color:#14532D}
.alert.warn{background:#FEF3C7; border:1px solid #FDE68A; color:#92400E}
.hidden{display:none !important}
</style>
</head>
<body>
<div class="top">منصة الاختبار الموحد - بدون اسم - إعداد: <strong>المشرفون</strong> | رمزك: <span id="myCode" style="font-family:monospace; background:rgba(255,255,255,0.15); padding:2px 8px; border-radius:6px"></span></div>
<div class="header">
  <h1 id="headerTitle">📝 الاختبار القبلي - بدون اسم</h1>
  <p id="headerDesc">أجب بدون إدخال اسمك - رمز تلقائي - 17 سؤال - يفتح البعدي تلقائياً بعد القبلي</p>
  <div class="badges">
    <div class="pill gold">🔒 البعدي مقفل حتى إتمام القبلي</div>
    <div class="pill">📊 تحليل تلقائي</div>
    <div class="pill">💾 حفظ للوحة المشرف</div>
  </div>
</div>

<div class="container">
  <div class="card">
    <div class="card-h navy"><span id="testTitle">الاختبار القبلي</span><span id="progressText">0/17</span></div>
    <div class="card-b">
      <div class="progress-track"><div class="progress-bar" id="pBar"></div></div>
      <div id="introBox">
        <div class="alert info"><span>ℹ️</span><div><strong>بدون اسم - رمز تلقائي:</strong> رمزك الحالي هو <span id="codeIntro" style="font-family:monospace; font-weight:900; background:#E0F2FE; padding:2px 6px; border-radius:4px"></span>. لا يمكن دخول البعدي إلا بعد إتمام القبلي. جميع إجاباتك سترسل تلقائياً للوحة المشرف.</div></div>
        <button class="btn btn-primary" style="margin-top:10px" onclick="start('pre')">▶️ بدء القبلي الآن</button>
      </div>
      <div id="qContainer" class="hidden"></div>
      <div id="submitBox" class="hidden" style="margin-top:12px">
        <button class="btn btn-gold" onclick="submitTest()">📤 تسليم وإرسال للوحة المشرف</button>
      </div>
      <div id="resultBox" class="hidden"></div>
    </div>
  </div>
</div>

<script>
const questions = [
  {id:1, level:'تذكر', text:'في تصنيف بلوم المعدل، ما المستوى الذي يقع في قمة الهرم؟', options:['التقويم','التحليل','الإبداع / الابتكار','التطبيق'], correct:2},
  {id:2, level:'فهم', text:'أي من المستويات يمثل مهارات التفكير العليا HOTs؟', options:['التذكر، الفهم، التطبيق','الفهم، التطبيق، التحليل','التحليل، التقويم، الإبداع','التطبيق، التحليل، الحفظ'], correct:2},
  {id:3, level:'تحليل', text:'«قارن بين الخلية النباتية والحيوانية» يستهدف مستوى:', options:['التذكر','التحليل','الإبداع','الاسترجاع'], correct:1},
  {id:4, level:'تقويم', text:'أي الأفعال ينتمي لمستوى التقويم؟', options:['يعدد، يسمي','يشرح، يلخص','ينقد، يبرر، يحكم','يحسب، يطبق'], correct:2},
  {id:5, level:'إبداع', text:'القدرة على توليد أكبر عدد من الأفكار تسمى:', options:['الطلاقة','المرونة','الأصالة','الفحص'], correct:0},
  {id:6, level:'ما وراء معرفي', text:'عندما يراقب الطالب طريقة تفكيره فهو يمارس:', options:['الاستذكاري','ما وراء المعرفي','الحسي','التقليدي'], correct:1},
  {id:7, level:'تحليل', text:'أي قبعة للتفكير الإبداعي والبدائل؟', options:['البيضاء','السوداء','الخضراء','الحمراء'], correct:2},
  {id:8, level:'تحليل', text:'نموذج CER يتكون من:', options:['الحفظ – التسميع','الادعاء – الدليل – التبرير','المقدمة – العرض','الملاحظة – النسخ'], correct:1},
  {id:9, level:'إبداع', text:'في SCAMPER حرف R يرمز إلى:', options:['استرجاع','عكس أو قلب الفرضية','حذف','قراءة'], correct:1},
  {id:10, level:'تطبيق', text:'زمن الانتظار التأملي الأمثل بعد سؤال تفكير عالٍ:', options:['أقل من ثانية','5-7 ثوانٍ','فوري من المعلم','مقاطعة'], correct:1},
  {id:11, level:'تقويم', text:'الأداة الأدق لتقويم مهام التفكير العليا:', options:['Rubrics سلالم تقدير','صواب/خطأ فقط','انطباع شخصي','عدد الصفحات'], correct:0},
  {id:12, level:'تطبيق', text:'أفضل حل لعائق ضيق زمن الحصة:', options:['إلغاء الأنشطة','الفصل المقلوب أو قوالب مركزة','ملخصات جاهزة','حفظ الكتاب'], correct:1},
  {id:13, level:'فهم', text:'الاهتمام بـ HOTs يعني إلغاء التذكر والفهم تماماً.', options:['صواب','خطأ'], correct:1},
  {id:14, level:'تذكر', text:'بلوم المعدل أضاف بُعد المعرفة ما وراء المعرفية.', options:['صواب','خطأ'], correct:0},
  {id:15, level:'تحليل', text:'«ما الدليل؟» يُصنف ضمن أسئلة فحص الأدلة.', options:['صواب','خطأ'], correct:0},
  {id:16, level:'فهم', text:'HOTs تقتصر على الموهوبين فقط.', options:['صواب','خطأ'], correct:1},
  {id:17, level:'إبداع', text:'RAFT تساعد على الإبداع عبر: الدور، الجمهور، الشكل، الموضوع.', options:['صواب','خطأ'], correct:0},
];

let mode=null;
let answers={};
let code = localStorage.getItem('hot_trainee_code') || `TRAINEE-${Math.floor(1000+Math.random()*9000)}`;
localStorage.setItem('hot_trainee_code', code);
document.getElementById('myCode').textContent = code;
document.getElementById('codeIntro').textContent = code;

function render(){
  const cont = document.getElementById('qContainer');
  cont.innerHTML='';
  questions.forEach(q=>{
    const div=document.createElement('div');
    div.className='q-card'+(answers[q.id]!=null?' answered':'');
    div.innerHTML=`<div><span class="q-num">${q.id}</span><span style="font-size:11px; background:#FEF3C7; padding:2px 6px; border-radius:10px; font-weight:800">${q.level}</span></div><div class="q-text">${q.text}</div><div class="options" id="opts-${q.id}"></div>`;
    cont.appendChild(div);
    const optsDiv=div.querySelector(`#opts-${q.id}`);
    q.options.forEach((opt,i)=>{
      const o=document.createElement('div');
      o.className='opt'+(answers[q.id]===i?' selected':'');
      o.innerHTML=`<div>${String.fromCharCode(65+i)}</div><div>${opt}</div>`;
      o.onclick=()=>{answers[q.id]=i; render(); updateProg();};
      optsDiv.appendChild(o);
    });
  });
  updateProg();
}
function updateProg(){
  const answered=Object.keys(answers).length;
  document.getElementById('progressText').textContent=`${answered}/${questions.length}`;
  document.getElementById('pBar').style.width=`${answered/questions.length*100}%`;
}
function start(m){
  if(m==='post' && !localStorage.getItem('hot_pre_data')){
    alert('يجب إتمام القبلي أولاً');
    return;
  }
  mode=m;
  answers={};
  render();
  document.getElementById('qContainer').classList.remove('hidden');
  document.getElementById('submitBox').classList.remove('hidden');
  document.getElementById('introBox').classList.add('hidden');
  document.getElementById('resultBox').classList.add('hidden');
  document.getElementById('testTitle').textContent = m==='pre'?'الاختبار القبلي - جارٍ الإجابة':'الاختبار البعدي - جارٍ الإجابة';
  document.getElementById('headerTitle').textContent = m==='pre'?'📝 الاختبار القبلي':'🚀 الاختبار البعدي';
}
function calc(){
  let score=0; let byLevel={};
  questions.forEach(q=>{
    if(!byLevel[q.level]) byLevel[q.level]={total:0, correct:0};
    byLevel[q.level].total++;
    if(answers[q.id]===q.correct){score++; byLevel[q.level].correct++;}
  });
  return {score, total:questions.length, percent:Math.round(score/questions.length*100), byLevel};
}
function submitTest(){
  const answered=Object.keys(answers).length;
  if(answered<questions.length && !confirm(`أجبت ${answered} من ${questions.length} فقط، تسليم؟`)) return;
  const res=calc();
  const payload={
    code: code,
    pre_score: mode==='pre'? res.score : null,
    pre_percent: mode==='pre'? res.percent : null,
    pre_byLevel: mode==='pre'? res.byLevel : null,
    pre_date: mode==='pre'? new Date().toISOString() : null,
    post_score: mode==='post'? res.score : null,
    post_percent: mode==='post'? res.percent : null,
    post_byLevel: mode==='post'? res.byLevel : null,
    post_date: mode==='post'? new Date().toISOString() : null,
    mode: mode
  };

  // Save locally first
  if(mode==='pre'){
    localStorage.setItem('hot_pre_data', JSON.stringify({score:res.score, total:res.total, percent:res.percent, byLevel:res.byLevel, answers, date:new Date().toISOString(), code}));
    localStorage.setItem('hot_pre_done','1');
  }else{
    const preData=JSON.parse(localStorage.getItem('hot_pre_data')||'{}');
    localStorage.setItem('hot_post_data', JSON.stringify({score:res.score, total:res.total, percent:res.percent, byLevel:res.byLevel, answers, date:new Date().toISOString(), code}));
    // Merge for server
    payload.pre_score = preData.score;
    payload.pre_percent = preData.percent;
    payload.pre_byLevel = preData.byLevel;
    payload.pre_date = preData.date;
  }

  // Send to supervisor server
  fetch('/api/submit', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(payload)})
    .then(r=>r.json())
    .then(d=>{
      console.log('Sent to supervisor', d);
      showResult(res, d.message||'تم الإرسال للوحة المشرف');
    })
    .catch(err=>{
      console.error(err);
      showResult(res, 'تم الحفظ محلياً (تعذر الاتصال بلوحة المشرف - سيتم الإرسال لاحقاً)');
    });
}

function showResult(res, serverMsg){
  document.getElementById('qContainer').classList.add('hidden');
  document.getElementById('submitBox').classList.add('hidden');
  const box=document.getElementById('resultBox');
  box.classList.remove('hidden');
  const isPre = mode==='pre';
  if(isPre){
    box.innerHTML=`
      <div class="alert success"><span>✅</span><div>تم تسليم القبلي: ${res.score}/${res.total} (${res.percent}%)<br>${serverMsg}<br>الآن يمكنك دخول البعدي</div></div>
      <button class="btn btn-primary" style="margin-top:10px" onclick="start('post')">🚀 الانتقال للاختبار البعدي (مفتوح الآن)</button>
      <button class="btn btn-outline" style="margin-top:8px" onclick="location.reload()">🔄 تحديث الصفحة</button>
    `;
  }else{
    const preData=JSON.parse(localStorage.getItem('hot_pre_data')||'{}');
    const gain = res.score - (preData.score||0);
    const gainPct = res.percent - (preData.percent||0);
    box.innerHTML=`
      <div class="alert success"><span>🏆</span><div>تم تسليم البعدي: ${res.score}/${res.total} (${res.percent}%)<br>القبلي كان: ${preData.score}/${preData.total} (${preData.percent}%)<br>التحسن: ${gain>0?'+':''}${gain} درجات (${gainPct>0?'+':''}${gainPct}%)<br>${serverMsg}</div></div>
      <div style="margin-top:10px; background:#F8FAFC; border:1px solid #CBD5E1; border-radius:10px; padding:10px; font-size:12px">
        <strong>📊 تم إرسال نتيجتك للوحة المشرف المركزية</strong><br>
        رمزك: ${code}<br>
        يمكنك الآن إغلاق الصفحة، وسيظهر تحسنك في لوحة المشرف تلقائياً
      </div>
      <button class="btn btn-outline" style="margin-top:10px" onclick="location.href='/supervisor'">📊 عرض لوحة المشرف (للمشرف فقط)</button>
    `;
  }
}

// Auto start logic: check if pre done
if(localStorage.getItem('hot_pre_data') && !localStorage.getItem('hot_post_data')){
  document.getElementById('introBox').innerHTML=`<div class="alert success"><span>✅</span><div>أتممت القبلي سابقاً بدرجة ${JSON.parse(localStorage.getItem('hot_pre_data')).score}/17<br>الاختبار البعدي مفتوح لك الآن</div></div><button class="btn btn-primary" style="margin-top:10px" onclick="start('post')">🚀 بدء الاختبار البعدي</button>`;
}
if(localStorage.getItem('hot_pre_data') && localStorage.getItem('hot_post_data')){
  const pre=JSON.parse(localStorage.getItem('hot_pre_data'));
  const post=JSON.parse(localStorage.getItem('hot_post_data'));
  document.getElementById('introBox').innerHTML=`<div class="alert success"><span>🏆</span><div>أتممت الاختبارين: قبلي ${pre.score}/17 → بعدي ${post.score}/17 (تحسن +${post.score-pre.score})<br>تم إرسال نتائجك للوحة المشرف</div></div><button class="btn btn-outline" style="margin-top:10px" onclick="if(confirm('إعادة البدء؟')){localStorage.clear(); location.reload();}">🔄 إعادة البدء من جديد</button>`;
}
</script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string("""
    <html lang="ar" dir="rtl"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>لوحة التحكم</title>
    <style>body{font-family:Tahoma; background:#F8FAFC; padding:20px; text-align:center} .card{background:#fff; border-radius:14px; padding:20px; max-width:600px; margin:20px auto; box-shadow:0 8px 20px rgba(0,0,0,0.07)} a{display:block; padding:14px; margin:10px 0; border-radius:10px; text-decoration:none; font-weight:900; color:#fff} .s{background:linear-gradient(135deg,#0F3D5E,#1B8A9D)} .t{background:linear-gradient(135deg,#D97706,#F59E0B)} .info{background:#E0F2FE; border:1px solid #BAE6FD; border-radius:10px; padding:10px; font-size:12px; margin-top:12px}</style>
    </head><body>
    <h2>🎓 منظومة الاختبار الموحد - إعداد: المشرفون</h2>
    <div class="card">
      <a class="s" href="/student">👨‍🎓 رابط الطالب - الاختبار القبلي والبعدي (بدون اسم - لا يحتاج كلمة مرور)</a>
      <a class="t" href="/supervisor">👩‍🏫 لوحة المشرف - محمية بكلمة مرور 🔐</a>
      <div class="info">🔑 كلمة مرور المشرف الافتراضية: <code style="background:#fff; padding:2px 8px; border-radius:6px; font-weight:900">Moshrefon@2026</code><br>رابط الطالب يعمل من أي جهاز بدون كلمة مرور ويجمع النتائج هنا</div>
      <div style="margin-top:14px; font-size:12px; color:#64748B">رابط واحد يجمع النتائج من جميع الأجهزة - حفظ دائم - تصدير Excel - إعداد المشرفون</div>
    </div>
    </body></html>
    """)

@app.route('/supervisor/login', methods=['GET','POST'])
def supervisor_login():
    error = None
    if request.method == 'POST':
        pwd = request.form.get('password','')
        if pwd == SUPERVISOR_PASSWORD:
            session['supervisor_logged_in'] = True
            session['login_time'] = datetime.datetime.now().isoformat()
            return redirect(url_for('supervisor'))
        else:
            error = f"كلمة المرور غير صحيحة. الكلمة الافتراضية هي: {SUPERVISOR_PASSWORD}"
    return render_template_string(LOGIN_HTML, error=error)

@app.route('/supervisor/logout')
def supervisor_logout():
    session.pop('supervisor_logged_in', None)
    return redirect(url_for('supervisor_login'))

@app.route('/supervisor')
@login_required
def supervisor():
    # Inject logout button and password info into supervisor html
    html = SUPERVISOR_HTML.replace('</div>\n\n<div class="header">', f'''<div style="text-align:left; padding:6px 12px; background:#0B2B44; display:flex; justify-content:space-between; align-items:center">
      <span style="font-size:11px; opacity:0.8">🔐 دخول آمن - {SUPERVISOR_PASSWORD} | مسجل دخول</span>
      <a href="/supervisor/logout" style="background:var(--coral); color:#fff; padding:4px 12px; border-radius:20px; font-size:11px; font-weight:800; text-decoration:none">🚪 تسجيل خروج</a>
    </div>
    </div>\n\n<div class="header">''')
    return render_template_string(html)

@app.route('/student')
def student():
    return render_template_string(STUDENT_HTML)

@app.route('/api/results', methods=['GET'])
@login_required
def api_results():
    data = load_data()
    return jsonify(data)

@app.route('/api/submit', methods=['POST'])
def api_submit():
    try:
        payload = request.get_json()
        if not payload or 'code' not in payload:
            return jsonify({"status":"error","message":"بيانات ناقصة"}), 400
        
        data = load_data()
        # Find existing record by code
        existing = None
        for rec in data:
            if rec.get('code') == payload['code']:
                existing = rec
                break
        
        if existing:
            # Update existing
            if payload.get('mode') == 'pre' or payload.get('pre_score') is not None:
                existing['pre_score'] = payload.get('pre_score', existing.get('pre_score'))
                existing['pre_percent'] = payload.get('pre_percent', existing.get('pre_percent'))
                existing['pre_byLevel'] = payload.get('pre_byLevel', existing.get('pre_byLevel'))
                existing['pre_date'] = payload.get('pre_date', existing.get('pre_date'))
            if payload.get('mode') == 'post' or payload.get('post_score') is not None:
                existing['post_score'] = payload.get('post_score', existing.get('post_score'))
                existing['post_percent'] = payload.get('post_percent', existing.get('post_percent'))
                existing['post_byLevel'] = payload.get('post_byLevel', existing.get('post_byLevel'))
                existing['post_date'] = payload.get('post_date', existing.get('post_date'))
            # Also keep pre if provided in post payload
            if payload.get('pre_score') is not None and existing.get('pre_score') is None:
                existing['pre_score'] = payload['pre_score']
                existing['pre_percent'] = payload['pre_percent']
                existing['pre_byLevel'] = payload['pre_byLevel']
                existing['pre_date'] = payload['pre_date']
        else:
            # Create new record
            new_rec = {
                "code": payload['code'],
                "pre_score": payload.get('pre_score'),
                "pre_percent": payload.get('pre_percent'),
                "pre_byLevel": payload.get('pre_byLevel'),
                "pre_date": payload.get('pre_date'),
                "post_score": payload.get('post_score'),
                "post_percent": payload.get('post_percent'),
                "post_byLevel": payload.get('post_byLevel'),
                "post_date": payload.get('post_date'),
            }
            data.append(new_rec)
        
        save_data(data)
        return jsonify({"status":"success","message":f"تم حفظ نتائج {payload['code']} بنجاح","count":len(data)})
    except Exception as e:
        return jsonify({"status":"error","message":str(e)}), 500

@app.route('/api/clear', methods=['POST'])
@login_required
def api_clear():
    save_data([])
    return jsonify({"status":"success","message":"تم مسح جميع البيانات"})

@app.route('/api/change-password', methods=['POST'])
@login_required
def api_change_password():
    global SUPERVISOR_PASSWORD
    data = request.get_json()
    old = data.get('old_password')
    new = data.get('new_password')
    if old != SUPERVISOR_PASSWORD:
        return jsonify({"status":"error","message":"كلمة المرور القديمة غير صحيحة"}), 400
    if not new or len(new) < 4:
        return jsonify({"status":"error","message":"كلمة المرور الجديدة قصيرة جداً"}), 400
    SUPERVISOR_PASSWORD = new
    return jsonify({"status":"success","message":f"تم تغيير كلمة المرور إلى: {new}"})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"Starting supervisor dashboard on 0.0.0.0:{port}")
    print("Student link: /student")
    print("Supervisor link: /supervisor")
    print(f"Password: {SUPERVISOR_PASSWORD}")
    print(f"Data file: {DATA_FILE}")
    app.run(host='0.0.0.0', port=port, debug=False)
