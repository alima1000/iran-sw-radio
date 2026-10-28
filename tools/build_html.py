#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Builds the standalone, fully-offline HTML application:
  app/Iran-SW-Radio-Guide.html
Contains 100% embedded data, styles, scripts, and SVG icons.
Includes the Offline-First Hybrid Update Center (Online fetch, File upload, Text paste, Export HTML, Reset).
Zero external dependencies, zero mandatory network calls.
"""

import os
import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
APP_DIR = os.path.join(BASE_DIR, 'app')
os.makedirs(APP_DIR, exist_ok=True)

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Iran SW Radio — راهنمای جامع و آفلاین رادیوهای موج کوتاه</title>
  <meta name="description" content="سامانه آفلاین و مستقل شناسایی فرکانس‌ها و جدول پخش رادیوهای موج کوتاه (SW) به وقت تهران با قابلیت به‌روزرسانی چندگانه">
  <style>
    /* -------------------------------------------------------------
       OFFLINE EMBEDDED STYLES - ZERO CDN - CLEAN RESPONSIVE RTL
       ------------------------------------------------------------- */
    :root {
      --bg-primary: #0d1117;
      --bg-secondary: #161b22;
      --bg-card: #21262d;
      --bg-card-hover: #29303a;
      --border-color: #30363d;
      --text-primary: #f0f6fc;
      --text-secondary: #8b949e;
      --text-muted: #6e7681;
      --accent: #58a6ff;
      --accent-hover: #79c0ff;
      --accent-bg: rgba(56, 139, 253, 0.15);
      --success: #3fb950;
      --success-bg: rgba(63, 185, 80, 0.15);
      --warning: #d29922;
      --warning-bg: rgba(210, 153, 34, 0.15);
      --danger: #f85149;
      --danger-bg: rgba(248, 81, 73, 0.15);
      --purple: #bc8cff;
      --purple-bg: rgba(188, 140, 255, 0.15);
      --font-family: 'Vazirmatn', -apple-system, BlinkMacSystemFont, 'Segoe UI', Tahoma, Arial, sans-serif;
      --shadow-sm: 0 1px 2px rgba(0,0,0,0.3);
      --shadow-md: 0 4px 12px rgba(0,0,0,0.4);
      --radius-sm: 6px;
      --radius-md: 10px;
      --radius-lg: 16px;
      --transition: all 0.2s ease;
    }

    [data-theme="light"] {
      --bg-primary: #f6f8fa;
      --bg-secondary: #ffffff;
      --bg-card: #ffffff;
      --bg-card-hover: #f3f4f6;
      --border-color: #d0d7de;
      --text-primary: #1f2328;
      --text-secondary: #57606a;
      --text-muted: #8c959f;
      --accent: #0969da;
      --accent-hover: #0550ae;
      --accent-bg: rgba(9, 105, 218, 0.1);
      --success: #1a7f37;
      --success-bg: rgba(26, 127, 55, 0.1);
      --warning: #9a6700;
      --warning-bg: rgba(154, 103, 0, 0.1);
      --danger: #cf222e;
      --danger-bg: rgba(207, 34, 46, 0.1);
      --purple: #8250df;
      --purple-bg: rgba(130, 80, 223, 0.1);
      --shadow-sm: 0 1px 3px rgba(0,0,0,0.08);
      --shadow-md: 0 4px 14px rgba(0,0,0,0.1);
    }

    /* Emergency Mode */
    body.emergency-mode {
      --bg-primary: #000000;
      --bg-secondary: #0a0a0a;
      --bg-card: #121212;
      --border-color: #e5a00d;
      --accent: #ffcc00;
      --text-primary: #ffffff;
      --text-secondary: #e0e0e0;
      font-size: 110%;
    }
    body.emergency-mode .non-emergency {
      display: none !important;
    }
    body.emergency-mode .emergency-banner {
      display: block !important;
    }

    * {
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }

    body {
      font-family: var(--font-family);
      background-color: var(--bg-primary);
      color: var(--text-primary);
      line-height: 1.7;
      direction: rtl;
      text-align: right;
      padding-bottom: 60px;
      transition: background-color 0.3s ease, color 0.3s ease;
    }

    a {
      color: var(--accent);
      text-decoration: none;
    }
    a:hover {
      text-decoration: underline;
    }

    .container {
      max-width: 1400px;
      margin: 0 auto;
      padding: 0 20px;
    }

    /* HEADER */
    header {
      background: var(--bg-secondary);
      border-bottom: 1px solid var(--border-color);
      padding: 18px 0;
      position: sticky;
      top: 0;
      z-index: 100;
      box-shadow: var(--shadow-sm);
    }

    .header-content {
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
    }

    .logo-area {
      display: flex;
      align-items: center;
      gap: 14px;
    }

    .radio-icon-box {
      width: 48px;
      height: 48px;
      background: linear-gradient(135deg, var(--accent), var(--purple));
      border-radius: var(--radius-md);
      display: flex;
      align-items: center;
      justify-content: center;
      color: #fff;
      box-shadow: var(--shadow-sm);
      flex-shrink: 0;
    }

    .title-group h1 {
      font-size: 22px;
      font-weight: 800;
      color: var(--text-primary);
      display: flex;
      align-items: center;
      gap: 10px;
    }

    .title-group p {
      font-size: 13px;
      color: var(--text-secondary);
    }

    .header-widgets {
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      gap: 10px;
    }

    .clock-widget {
      background: var(--bg-card);
      border: 1px solid var(--border-color);
      padding: 8px 16px;
      border-radius: var(--radius-md);
      display: flex;
      align-items: center;
      gap: 12px;
    }

    .clock-icon {
      color: var(--accent);
    }

    .clock-time {
      font-size: 20px;
      font-weight: 800;
      font-variant-numeric: tabular-nums;
      color: var(--text-primary);
      letter-spacing: 0.5px;
    }

    .clock-meta {
      font-size: 11px;
      color: var(--text-secondary);
      line-height: 1.3;
    }

    .status-badge {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 6px 12px;
      border-radius: 20px;
      font-size: 12px;
      font-weight: 600;
    }

    .status-badge.offline {
      background: var(--success-bg);
      color: var(--success);
      border: 1px solid var(--success);
    }

    .status-badge.offline::before {
      content: "";
      width: 8px;
      height: 8px;
      background: var(--success);
      border-radius: 50%;
      display: inline-block;
      animation: pulse 2s infinite;
    }

    @keyframes pulse {
      0% { opacity: 1; transform: scale(1); }
      50% { opacity: 0.4; transform: scale(0.9); }
      100% { opacity: 1; transform: scale(1); }
    }

    .btn {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      padding: 8px 14px;
      border-radius: var(--radius-sm);
      font-size: 13px;
      font-weight: 600;
      font-family: inherit;
      cursor: pointer;
      border: 1px solid var(--border-color);
      background: var(--bg-card);
      color: var(--text-primary);
      transition: var(--transition);
    }

    .btn:hover {
      background: var(--bg-card-hover);
      border-color: var(--accent);
    }

    .btn-emergency {
      background: var(--danger-bg);
      color: var(--danger);
      border-color: var(--danger);
      font-weight: 800;
    }
    .btn-emergency:hover {
      background: var(--danger);
      color: #fff;
    }

    .btn-accent {
      background: var(--accent);
      color: #fff;
      border-color: var(--accent);
    }
    .btn-accent:hover {
      background: var(--accent-hover);
    }

    .btn-success {
      background: var(--success);
      color: #fff;
      border-color: var(--success);
    }
    .btn-success:hover {
      filter: brightness(1.1);
    }

    /* EMERGENCY BANNER */
    .emergency-banner {
      display: none;
      background: #7a1414;
      color: #ffffff;
      padding: 12px;
      text-align: center;
      font-size: 15px;
      font-weight: 700;
      border-bottom: 2px solid #ffcc00;
    }

    /* STATS STRIP */
    .stats-strip {
      margin: 20px 0;
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 12px;
    }

    .stat-card {
      background: var(--bg-secondary);
      border: 1px solid var(--border-color);
      padding: 14px 18px;
      border-radius: var(--radius-md);
      display: flex;
      align-items: center;
      justify-content: space-between;
      box-shadow: var(--shadow-sm);
    }

    .stat-title {
      font-size: 13px;
      color: var(--text-secondary);
    }

    .stat-val {
      font-size: 22px;
      font-weight: 800;
      color: var(--accent);
    }

    /* NAVIGATION TABS */
    .nav-tabs {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      background: var(--bg-secondary);
      padding: 8px;
      border-radius: var(--radius-md);
      border: 1px solid var(--border-color);
      margin-bottom: 20px;
    }

    .nav-tab {
      padding: 10px 18px;
      border-radius: var(--radius-sm);
      font-size: 14px;
      font-weight: 700;
      color: var(--text-secondary);
      background: transparent;
      border: none;
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 8px;
      transition: var(--transition);
      font-family: inherit;
    }

    .nav-tab:hover {
      color: var(--text-primary);
      background: var(--bg-card-hover);
    }

    .nav-tab.active {
      background: var(--accent-bg);
      color: var(--accent);
      border: 1px solid var(--accent);
    }

    /* CONTROLS (SEARCH & FILTERS) */
    .controls-panel {
      background: var(--bg-secondary);
      border: 1px solid var(--border-color);
      border-radius: var(--radius-md);
      padding: 18px;
      margin-bottom: 22px;
      box-shadow: var(--shadow-sm);
    }

    .search-row {
      display: flex;
      gap: 12px;
      margin-bottom: 16px;
    }

    .search-box {
      position: relative;
      flex: 1;
    }

    .search-input {
      width: 100%;
      padding: 12px 44px 12px 16px;
      background: var(--bg-card);
      border: 1px solid var(--border-color);
      border-radius: var(--radius-sm);
      color: var(--text-primary);
      font-size: 15px;
      font-family: inherit;
      outline: none;
      transition: var(--transition);
    }

    .search-input:focus {
      border-color: var(--accent);
      box-shadow: 0 0 0 3px var(--accent-bg);
    }

    .search-icon {
      position: absolute;
      right: 14px;
      top: 50%;
      transform: translateY(-50%);
      color: var(--text-muted);
      pointer-events: none;
    }

    .filters-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
      gap: 12px;
      align-items: center;
    }

    .filter-item label {
      display: block;
      font-size: 12px;
      font-weight: 600;
      color: var(--text-secondary);
      margin-bottom: 4px;
    }

    .filter-select {
      width: 100%;
      padding: 8px 12px;
      background: var(--bg-card);
      border: 1px solid var(--border-color);
      border-radius: var(--radius-sm);
      color: var(--text-primary);
      font-size: 13px;
      font-family: inherit;
      outline: none;
      cursor: pointer;
    }

    .filter-select:focus {
      border-color: var(--accent);
    }

    /* TAB CONTENTS */
    .tab-content {
      display: none;
    }
    .tab-content.active {
      display: block;
    }

    /* CARDS & GRIDS */
    .schedule-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
      gap: 16px;
    }

    .schedule-card {
      background: var(--bg-secondary);
      border: 1px solid var(--border-color);
      border-radius: var(--radius-md);
      padding: 18px;
      box-shadow: var(--shadow-sm);
      transition: var(--transition);
      display: flex;
      flex-direction: column;
      position: relative;
    }

    .schedule-card:hover {
      transform: translateY(-2px);
      box-shadow: var(--shadow-md);
      border-color: var(--accent);
    }

    .card-top {
      display: flex;
      align-items: flex-start;
      justify-content: space-between;
      gap: 12px;
      margin-bottom: 12px;
    }

    .freq-badge {
      background: var(--accent-bg);
      color: var(--accent);
      border: 1px solid var(--accent);
      padding: 4px 10px;
      border-radius: var(--radius-sm);
      font-size: 18px;
      font-weight: 800;
      letter-spacing: 0.5px;
      display: inline-flex;
      align-items: center;
      gap: 6px;
    }

    .band-pill {
      font-size: 11px;
      font-weight: 600;
      padding: 3px 8px;
      border-radius: 12px;
      background: var(--bg-card);
      color: var(--text-secondary);
      border: 1px solid var(--border-color);
    }

    .station-name {
      font-size: 16px;
      font-weight: 700;
      color: var(--text-primary);
      margin-bottom: 2px;
    }

    .program-title {
      font-size: 13px;
      color: var(--text-secondary);
      margin-bottom: 12px;
    }

    .card-meta-list {
      display: flex;
      flex-direction: column;
      gap: 6px;
      font-size: 13px;
      margin-bottom: 14px;
      border-top: 1px dashed var(--border-color);
      padding-top: 10px;
    }

    .meta-row {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 8px;
    }

    .meta-label {
      color: var(--text-muted);
      display: flex;
      align-items: center;
      gap: 6px;
    }

    .meta-value {
      font-weight: 600;
      color: var(--text-primary);
    }

    .badge-conf {
      display: inline-block;
      padding: 2px 8px;
      border-radius: 4px;
      font-size: 11px;
      font-weight: 700;
    }
    .badge-conf-A {
      background: var(--success-bg);
      color: var(--success);
      border: 1px solid var(--success);
    }
    .badge-conf-B {
      background: var(--accent-bg);
      color: var(--accent);
      border: 1px solid var(--accent);
    }
    .badge-conf-C {
      background: var(--warning-bg);
      color: var(--warning);
      border: 1px solid var(--warning);
    }
    .badge-conf-D {
      background: var(--danger-bg);
      color: var(--danger);
      border: 1px solid var(--danger);
    }

    .card-footer {
      margin-top: auto;
      border-top: 1px solid var(--border-color);
      padding-top: 10px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 8px;
    }

    .alts-tag-box {
      font-size: 12px;
      color: var(--text-secondary);
      margin-bottom: 10px;
    }

    .alts-pill {
      display: inline-block;
      background: var(--bg-card);
      border: 1px solid var(--border-color);
      padding: 2px 6px;
      border-radius: 4px;
      margin: 2px;
      font-weight: 600;
      cursor: pointer;
    }
    .alts-pill:hover {
      border-color: var(--accent);
      color: var(--accent);
    }

    .star-btn {
      background: transparent;
      border: none;
      color: var(--text-muted);
      cursor: pointer;
      font-size: 18px;
      transition: var(--transition);
      line-height: 1;
    }
    .star-btn.starred {
      color: #e3b341;
    }

    /* TABLES */
    .table-container {
      overflow-x: auto;
      background: var(--bg-secondary);
      border: 1px solid var(--border-color);
      border-radius: var(--radius-md);
      box-shadow: var(--shadow-sm);
    }

    table.data-table {
      width: 100%;
      border-collapse: collapse;
      text-align: right;
      font-size: 13px;
    }

    table.data-table th {
      background: var(--bg-card);
      color: var(--text-secondary);
      font-weight: 700;
      padding: 12px 14px;
      border-bottom: 2px solid var(--border-color);
      white-space: nowrap;
    }

    table.data-table td {
      padding: 12px 14px;
      border-bottom: 1px solid var(--border-color);
      color: var(--text-primary);
    }

    table.data-table tr:hover td {
      background: var(--bg-card-hover);
    }

    /* 24-HOUR PLANNER */
    .hour-selector-bar {
      display: flex;
      align-items: center;
      gap: 8px;
      overflow-x: auto;
      padding: 12px;
      background: var(--bg-secondary);
      border: 1px solid var(--border-color);
      border-radius: var(--radius-md);
      margin-bottom: 20px;
    }

    .hour-btn {
      padding: 8px 14px;
      border-radius: var(--radius-sm);
      border: 1px solid var(--border-color);
      background: var(--bg-card);
      color: var(--text-primary);
      font-size: 14px;
      font-weight: 700;
      cursor: pointer;
      white-space: nowrap;
      transition: var(--transition);
      font-family: inherit;
    }

    .hour-btn:hover {
      border-color: var(--accent);
    }

    .hour-btn.active {
      background: var(--accent);
      color: #fff;
      border-color: var(--accent);
    }

    /* MODAL */
    .modal-overlay {
      display: none;
      position: fixed;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background: rgba(0,0,0,0.7);
      backdrop-filter: blur(4px);
      z-index: 1000;
      align-items: center;
      justify-content: center;
      padding: 20px;
    }
    .modal-overlay.open {
      display: flex;
    }

    .modal-card {
      background: var(--bg-secondary);
      border: 1px solid var(--border-color);
      border-radius: var(--radius-lg);
      max-width: 750px;
      width: 100%;
      max-height: 85vh;
      overflow-y: auto;
      padding: 24px;
      box-shadow: var(--shadow-md);
      position: relative;
    }

    .modal-close {
      position: absolute;
      top: 18px;
      left: 18px;
      background: transparent;
      border: none;
      color: var(--text-muted);
      font-size: 24px;
      cursor: pointer;
    }

    /* RECEPTION LOG FORM & UPDATE CENTER CARDS */
    .log-form-grid, .update-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
      gap: 16px;
      margin-bottom: 16px;
    }

    .update-card {
      background: var(--bg-card);
      border: 1px solid var(--border-color);
      border-radius: var(--radius-md);
      padding: 20px;
      display: flex;
      flex-direction: column;
      box-shadow: var(--shadow-sm);
      transition: var(--transition);
    }

    .update-card:hover {
      border-color: var(--accent);
    }

    .update-card-title {
      font-size: 16px;
      font-weight: 800;
      color: var(--accent);
      margin-bottom: 8px;
      display: flex;
      align-items: center;
      gap: 8px;
    }

    .update-card-desc {
      font-size: 13px;
      color: var(--text-secondary);
      margin-bottom: 14px;
      line-height: 1.8;
    }

    .drop-zone {
      border: 2px dashed var(--accent);
      background: var(--accent-bg);
      border-radius: var(--radius-sm);
      padding: 24px 16px;
      text-align: center;
      cursor: pointer;
      transition: var(--transition);
      margin-bottom: 12px;
    }
    .drop-zone:hover {
      background: rgba(56, 139, 253, 0.25);
    }

    .form-group label {
      display: block;
      font-size: 13px;
      font-weight: 600;
      margin-bottom: 6px;
      color: var(--text-secondary);
    }

    .form-control {
      width: 100%;
      padding: 10px 14px;
      background: var(--bg-card);
      border: 1px solid var(--border-color);
      border-radius: var(--radius-sm);
      color: var(--text-primary);
      font-family: inherit;
      font-size: 14px;
      outline: none;
    }

    .form-control:focus {
      border-color: var(--accent);
    }

    /* PRINT STYLES */
    @media print {
      header, .nav-tabs, .controls-panel, .btn, .header-widgets, .star-btn {
        display: none !important;
      }
      body {
        background: #fff !important;
        color: #000 !important;
        font-size: 10pt;
      }
      .tab-content {
        display: block !important;
      }
      .schedule-grid {
        display: block !important;
      }
      .schedule-card {
        page-break-inside: avoid;
        border: 1px solid #ccc !important;
        margin-bottom: 12px !important;
      }
      table.data-table th, table.data-table td {
        border: 1px solid #ddd !important;
        color: #000 !important;
      }
    }

    @media (max-width: 768px) {
      .title-group h1 {
        font-size: 18px;
      }
      .schedule-grid, .update-grid {
        grid-template-columns: 1fr;
      }
      .header-content {
        flex-direction: column;
        align-items: stretch;
      }
    }
  </style>
</head>
<body>

  <!-- EMERGENCY MODE BANNER -->
  <div class="emergency-banner">
    ⚠️ حالت اضطراری فعال است — فقط برنامه‌های حیاتی فارسی در حال پخش به وقت تهران نمایش داده می‌شوند.
  </div>

  <!-- HEADER -->
  <header>
    <div class="container header-content">
      <div class="logo-area">
        <div class="radio-icon-box" title="Iran SW Radio">
          <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M4.9 19.1C1 15.2 1 8.8 4.9 4.9"/>
            <path d="M7.8 16.2c-2.3-2.3-2.3-6.1 0-8.5"/>
            <circle cx="12" cy="12" r="2"/>
            <path d="M16.2 7.8c2.3 2.3 2.3 6.1 0 8.5"/>
            <path d="M19.1 4.9C23 8.8 23 15.1 19.1 19"/>
          </svg>
        </div>
        <div class="title-group">
          <h1>Iran SW Radio <span style="font-size: 14px; font-weight: normal; color: var(--accent);">راهنمای آفلاین موج کوتاه</span></h1>
          <p>مستقل از اینترنت و سرور • تنظیم دقیق به وقت رسمی تهران (UTC+03:30)</p>
        </div>
      </div>

      <div class="header-widgets">
        <!-- LIVE TEHRAN CLOCK WIDGET -->
        <div class="clock-widget">
          <svg class="clock-icon" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="10"/>
            <polyline points="12 6 12 12 16 14"/>
          </svg>
          <div>
            <div class="clock-time" id="tehran-time-display">--:--:--</div>
            <div class="clock-meta" id="tehran-date-display">ساعت تهران (UTC+03:30)</div>
          </div>
        </div>

        <div class="status-badge offline" id="app-offline-badge" title="این نرم‌افزار به صورت کاملاً محلی اجرا می‌شود و هیچ درخواستی به اینترنت ارسال نمی‌کند">
          آفلاین ۱۰۰٪
        </div>

        <button class="btn btn-accent" onclick="switchTab('tab-update')" title="مرکز به‌روزرسانی آنلاین و وارد کردن داده‌های جدید">
          🔄 به‌روزرسانی
        </button>

        <button class="btn btn-emergency" id="btn-toggle-emergency" title="حالت ساده و با کنتراست بالا برای شرایط بحرانی">
          🚨 حالت اضطراری
        </button>

        <button class="btn" id="btn-toggle-theme" title="تغییر تم روشن / تاریک">
          🌓
        </button>

        <button class="btn" onclick="window.print()" title="چاپ مستقیم این صفحه">
          🖨️ چاپ
        </button>
      </div>
    </div>
  </header>

  <main class="container" style="margin-top: 20px;">

    <!-- STATS STRIP -->
    <div class="stats-strip non-emergency">
      <div class="stat-card">
        <div>
          <div class="stat-title">تعداد شبکه‌ها</div>
          <div class="stat-val" id="stat-stations">۲۱</div>
        </div>
        <span>📻</span>
      </div>
      <div class="stat-card">
        <div>
          <div class="stat-title">کل رکوردهای پخش</div>
          <div class="stat-val" id="stat-schedules">۵۵</div>
        </div>
        <span>📡</span>
      </div>
      <div class="stat-card">
        <div>
          <div class="stat-title">برنامه‌های فارسی‌زبان</div>
          <div class="stat-val" style="color: var(--success);" id="stat-farsi">۴۱</div>
        </div>
        <span>🇮🇷</span>
      </div>
      <div class="stat-card">
        <div>
          <div class="stat-title">تأییدشده رسمی (HFCC)</div>
          <div class="stat-val" style="color: var(--purple);" id="stat-verified">۴۸</div>
        </div>
        <span>✅</span>
      </div>
      <div class="stat-card">
        <div>
          <div class="stat-title">نیازمند بررسی / اضطراری</div>
          <div class="stat-val" style="color: var(--warning);" id="stat-review">۷</div>
        </div>
        <span>⚠️</span>
      </div>
    </div>

    <!-- NAVIGATION TABS -->
    <nav class="nav-tabs" role="tablist">
      <button class="nav-tab active" data-tab="tab-now">
        🔴 در حال پخش طبق جدول
      </button>
      <button class="nav-tab" data-tab="tab-all">
        📋 کل برنامه‌ها (<span id="tab-all-count">۵۵</span>)
      </button>
      <button class="nav-tab" data-tab="tab-planner">
        ⏱️ نمای ۲۴ ساعته
      </button>
      <button class="nav-tab" data-tab="tab-hourly">
        📑 راهنمای ساعت‌به‌ساعت
      </button>
      <button class="nav-tab" data-tab="tab-freq">
        📶 مرور فرکانسی (kHz)
      </button>
      <button class="nav-tab" data-tab="tab-stations">
        🏢 شناسنامه شبکه‌ها
      </button>
      <button class="nav-tab" data-tab="tab-guide">
        📖 راهنمای تنظیم گیرنده و باندها
      </button>
      <button class="nav-tab" data-tab="tab-logs">
        📝 ثبت گزارش شنود (SINPO)
      </button>
      <button class="nav-tab" data-tab="tab-favorites">
        ⭐ علاقه‌مندی‌ها (<span id="fav-count">۰</span>)
      </button>
      <button class="nav-tab" data-tab="tab-update" style="border: 1px solid var(--accent); color: var(--accent);">
        🔄 مرکز به‌روزرسانی
      </button>
    </nav>

    <!-- SEARCH & FILTERS CONTROLS -->
    <section class="controls-panel">
      <div class="search-row">
        <div class="search-box">
          <svg class="search-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="11" cy="11" r="8"/>
            <line x1="21" y1="21" x2="16.65" y2="16.65"/>
          </svg>
          <input type="text" id="global-search-input" class="search-input" placeholder="جستوجوی سریع نام شبکه، فرکانس (کیلوهرتز)، زبان، کشور، فرستنده یا برنامه...">
        </div>
        <button class="btn" id="btn-reset-filters" title="پاک کردن تمام فیلترها">
          🔄 پاکسازی
        </button>
      </div>

      <div class="filters-grid">
        <div class="filter-item">
          <label for="filter-language">زبان برنامه:</label>
          <select id="filter-language" class="filter-select">
            <option value="all">همه زبان‌ها</option>
            <option value="farsi" selected>فقط زبان‌های فارسی (فارسی، دری، تاجیکی)</option>
            <option value="en">انگلیسی</option>
            <option value="ar">عربی</option>
            <option value="other">سایر زبان‌ها</option>
          </select>
        </div>

        <div class="filter-item">
          <label for="filter-category">دسته‌بندی محتوا:</label>
          <select id="filter-category" class="filter-select">
            <option value="all">همه دسته‌ها</option>
            <option value="news">فقط شبکه‌های خبری و تحلیلی</option>
            <option value="general">عمومی و منطقه‌ای</option>
            <option value="culture">فرهنگی و موسیقی</option>
            <option value="religious">مذهبی و نیایشی</option>
            <option value="opposition">سیاسی و اپوزیسیون</option>
          </select>
        </div>

        <div class="filter-item">
          <label for="filter-band">باند امواج رادیویی:</label>
          <select id="filter-band" class="filter-select">
            <option value="all">همه باندها</option>
            <option value="49m">باند ۴۹ متر (شبانگاهی اصلی)</option>
            <option value="41m">باند ۴۱ متر (عصر و غروب)</option>
            <option value="31m">باند ۳۱ متر (شب و روز)</option>
            <option value="25m">باند ۲۵ متر (بعدازظهر)</option>
            <option value="19m">باند ۱۹ متر (روزانه قوی)</option>
            <option value="MW">موج متوسط (MW / AM)</option>
          </select>
        </div>

        <div class="filter-item">
          <label for="filter-confidence">سطح اطمینان داده:</label>
          <select id="filter-confidence" class="filter-select">
            <option value="all">همه سطوح اعتبار</option>
            <option value="verified">سطح A و B (تأییدشده و معتبر)</option>
            <option value="review">سطح C و D (نیازمند بررسی / اضطراری)</option>
          </select>
        </div>

        <div class="filter-item">
          <label for="filter-sort">مرتب‌سازی نتایج:</label>
          <select id="filter-sort" class="filter-select">
            <option value="time-asc">ساعت شروع (تهران) - صعودی</option>
            <option value="freq-asc">فرکانس (kHz) - کم به زیاد</option>
            <option value="freq-desc">فرکانس (kHz) - زیاد به کم</option>
            <option value="name-asc">نام شبکه</option>
            <option value="conf-desc">سطح اطمینان (اول A)</option>
          </select>
        </div>
      </div>
    </section>

    <!-- TAB 1: NOW ON AIR -->
    <div id="tab-now" class="tab-content active">
      <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 16px; flex-wrap: wrap; gap: 10px;">
        <div>
          <h2 style="font-size: 18px; font-weight: 800; display: flex; align-items: center; gap: 8px;">
            <span style="color: var(--danger);">●</span> در حال پخش طبق جدول ثبت‌شده
          </h2>
          <p style="font-size: 13px; color: var(--text-secondary);">برنامه‌هایی که بر اساس ساعت رسمی تهران (<span id="now-time-indicator">--:--</span>) باید هم‌اکنون فعال باشند.</p>
        </div>
        <div style="display: flex; align-items: center; gap: 8px;">
          <label for="custom-time-picker" style="font-size: 13px; color: var(--text-secondary);">آزمایش ساعت دلخواه:</label>
          <input type="time" id="custom-time-picker" class="form-control" style="width: auto; padding: 6px 10px;">
          <button class="btn" id="btn-reset-custom-time" title="بازگشت به ساعت زنده تهران">ساعت فعلی</button>
        </div>
      </div>
      <div id="now-on-air-grid" class="schedule-grid"></div>
    </div>

    <!-- TAB 2: ALL SCHEDULES -->
    <div id="tab-all" class="tab-content">
      <div style="margin-bottom: 16px; display: flex; justify-content: space-between; align-items: center;">
        <h2 style="font-size: 18px; font-weight: 800;">فهرست جامع جدول پخش رادیوها</h2>
        <span style="font-size: 13px; color: var(--text-secondary);" id="all-count-display">نمایش -- رکورد</span>
      </div>
      <div id="all-schedules-grid" class="schedule-grid"></div>
    </div>

    <!-- TAB 3: 24-HOUR PLANNER -->
    <div id="tab-planner" class="tab-content">
      <div style="margin-bottom: 16px;">
        <h2 style="font-size: 18px; font-weight: 800;">نمای ۲۴ ساعته شبانه‌روز</h2>
        <p style="font-size: 13px; color: var(--text-secondary);">ساعت مورد نظر را انتخاب کنید تا تمام برنامه‌های در حال پخش در آن ساعت را مشاهده کنید.</p>
      </div>

      <div class="hour-selector-bar" id="hour-selector-container"></div>

      <div style="margin-bottom: 14px; font-weight: 700; color: var(--accent);" id="planner-hour-header">
        برنامه‌های فعال در ساعت انتخاب‌شده:
      </div>
      <div id="planner-schedules-grid" class="schedule-grid"></div>
    </div>

    <!-- TAB 4: HOURLY EMERGENCY MATRIX -->
    <div id="tab-hourly" class="tab-content">
      <div style="margin-bottom: 16px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
        <div>
          <h2 style="font-size: 18px; font-weight: 800;">راهنمای ساعت‌به‌ساعت (مناسب شرایط اضطراری و چاپ)</h2>
          <p style="font-size: 13px; color: var(--text-secondary);">تمام ۲۴ ساعت شبانه‌روز با تفکیک فرکانس‌ها و ایستگاه‌های فعال</p>
        </div>
        <button class="btn btn-accent" onclick="window.print()">🖨️ چاپ این جدول</button>
      </div>

      <div id="hourly-matrix-container"></div>
    </div>

    <!-- TAB 5: FREQUENCY SPECTRUM BROWSER -->
    <div id="tab-freq" class="tab-content">
      <div style="margin-bottom: 16px;">
        <h2 style="font-size: 18px; font-weight: 800;">مرور بر اساس طیف فرکانسی (kHz)</h2>
        <p style="font-size: 13px; color: var(--text-secondary);">مشاهده ایستگاه‌ها و جدول زمانی به ترتیب صعودی کیلوهرتز و باندهای امواج کوتاه</p>
      </div>

      <div class="table-container">
        <table class="data-table" id="freq-table">
          <thead>
            <tr>
              <th>فرکانس (kHz)</th>
              <th>باند امواج</th>
              <th>شبکه و برنامه</th>
              <th>زبان</th>
              <th>ساعت پخش (تهران)</th>
              <th>فرستنده / توان</th>
              <th>وضعیت اعتبار</th>
              <th>اقدام</th>
            </tr>
          </thead>
          <tbody id="freq-table-body"></tbody>
        </table>
      </div>
    </div>

    <!-- TAB 6: STATIONS DIRECTORY -->
    <div id="tab-stations" class="tab-content">
      <div style="margin-bottom: 16px;">
        <h2 style="font-size: 18px; font-weight: 800;">شناسنامه و وضعیت شبکه‌های رادیویی</h2>
        <p style="font-size: 13px; color: var(--text-secondary);">اطلاعات تفصیلی سازمان، کشور، وضعیت فرستنده موج کوتاه و تاریخچه فعالیت</p>
      </div>
      <div id="stations-grid" class="schedule-grid"></div>
    </div>

    <!-- TAB 7: GUIDE & RECEIVER TUTORIAL -->
    <div id="tab-guide" class="tab-content">
      <div style="max-width: 900px; margin: 0 auto; background: var(--bg-secondary); border: 1px solid var(--border-color); border-radius: var(--radius-lg); padding: 28px;">
        <h2 style="font-size: 22px; font-weight: 800; color: var(--accent); margin-bottom: 16px;">
          📻 راهنمای جامع دریافت امواج کوتاه (SW) در شرایط اضطراری و قطعی اینترنت
        </h2>
        <div style="margin-bottom: 24px; font-size: 15px; line-height: 2.0;">
          <h3 style="font-size: 17px; font-weight: 700; color: var(--text-primary); margin-top: 16px; margin-bottom: 8px;">۱. رادیو موج کوتاه چیست و چرا در زمان قطعی اینترنت از کار نمی‌افتد؟</h3>
          <p>امواج کوتاه (Shortwave یا به اختصار SW) به فرکانس‌های بین ۳ تا ۳۰ مگاهرتز (۳۰۰۰ تا ۳۰۰۰۰ کیلوهرتز) گفته می‌شود. برخلاف اینترنت و تلفن همراه که به فیبر نوری، دکل‌های برق شهری و سرورهای محلی وابسته‌اند، امواج کوتاه با بازتاب از لایه‌های یونوسفر زمین (یونوسفر در ارتفاع ۸۰ تا ۳۰۰ کیلومتری جو) هزاران کیلومتر مسافت را بدون واسطه طی می‌کنند و مستقیماً به آنتن رادیوی شما می‌رسند. هیچ نهاد داخلی نمی‌تواند کل امواج کوتاه آسمان را قطع کند.</p>

          <h3 style="font-size: 17px; font-weight: 700; color: var(--text-primary); margin-top: 18px; margin-bottom: 8px;">۲. واحد فرکانس و نحوه تنظیم رادیو</h3>
          <p>در رادیوهای آنالوگ عقربه‌ای و رادیوهای دیجیتال مدرن، فرکانس‌ها با واحد کیلوهرتز (kHz) یا مگاهرتز (MHz) نشان داده می‌شوند. هر ۱۰۰۰ کیلوهرتز برابر با ۱ مگاهرتز است. مثلاً فرکانس رادیو فردا روی <strong>5860 kHz</strong> برابر با <strong>5.86 MHz</strong> در باند ۴۹ متر است.</p>

          <h3 style="font-size: 17px; font-weight: 700; color: var(--text-primary); margin-top: 18px; margin-bottom: 8px;">۳. مدولاسیون و تنظیمات گیرنده</h3>
          <p>تمام برنامه‌های رادیویی عمومی مندرج در این راهنما با مدولاسیون استاندارد <strong>AM</strong> پخش می‌شوند. برای شنیدن آنها نیازی به گیرنده‌های گران‌قیمت مجهز به SSB یا USB/LSB ندارید؛ یک گیرنده ساده چندموج خانگی یا رادیوی خودرو کافی است.</p>

          <h3 style="font-size: 17px; font-weight: 700; color: var(--text-primary); margin-top: 18px; margin-bottom: 8px;">۴. اثر شب و روز بر امواج رادیویی (قانون طلایی فرکانس‌ها)</h3>
          <ul style="padding-right: 20px; margin-bottom: 12px;">
            <li><strong>در طول شب:</strong> لایه D یونوسفر از بین می‌رود و فرکانس‌های پایین‌تر (زیر ۱۰ مگاهرتز مثل باندهای ۴۹ متر و ۴۱ متر) به راحتی از فاصله چند هزار کیلومتری دریافت می‌شوند. بهترین زمان برای گوش دادن به ۵۸۶۰، ۵۸۹۰، ۷۴۱۵ و ۶۰۱۰ کیلوهرتز ساعات شب است.</li>
            <li><strong>در طول روز:</strong> تابش خورشید لایه‌های بالایی را یونیزه می‌کند و فرکانس‌های بالاتر (بالای ۱۲ مگاهرتز مانند باندهای ۲۵ متر، ۲۲ متر و ۱۹ متر مثل ۹۶۲۰، ۱۲۰۰۵، ۱۳۶۰۰ و ۱۵۷۲۰ کیلوهرتز) دریافت فوق‌العاده شفافی دارند.</li>
          </ul>

          <h3 style="font-size: 17px; font-weight: 700; color: var(--text-primary); margin-top: 18px; margin-bottom: 8px;">۵. راهکارهای ساده برای رفع نویز و تقویت ۵ برابری سیگنال</h3>
          <ol style="padding-right: 20px;">
            <li><strong>فاصله گرفتن از منابع پارازیت الکتریکی:</strong> شارژرهای موبایل، لامپ‌های LED بی‌کیفیت، آداپتورها و تلویزیون‌ها نویز وحشتناکی روی موج کوتاه ایجاد می‌کنند. رادیو را با باتری روشن کنید و از وسایل برقی حداقل ۳ متر فاصله بگیرید.</li>
            <li><strong>ساخت آنتن سیمی ساده (معجزه دریافت):</strong> یک رشته سیم نازک مسی معمولی (حتی سیم تلفن یا سیم روکش‌دار ساده) به طول ۳ تا ۵ متر آماده کنید. یک سر آن را دور آنتن تلسکوپی رادیو بپیچید و سر دیگر را به طرف پنجره، بالکن یا فضای باز هدایت کنید. این کار سیگنال‌های ضعیف را بسیار شفاف می‌کند.</li>
            <li><strong>تنظیم موقعیت و زاویه رادیو:</strong> رادیو را نزدیک پنجره‌ای قرار دهید که رو به جهت کشور فرستنده (مثلاً رو به غرب برای فرستنده‌های کویت و اروپا، یا رو به شرق برای چین و هند) باشد.</li>
          </ol>
        </div>

        <h3 style="font-size: 17px; font-weight: 700; color: var(--text-primary); margin-bottom: 12px;">جدول باندهای استاندارد موج کوتاه</h3>
        <div class="table-container">
          <table class="data-table">
            <thead>
              <tr>
                <th>نام باند</th>
                <th>محدوده فرکانس (kHz)</th>
                <th>بهترین ساعات شنود</th>
                <th>ویژگی انتشار امواج</th>
              </tr>
            </thead>
            <tbody>
              <tr><td>باند ۴۹ متر</td><td>5800 - 6200 kHz</td><td>شب تا سحرگاه (۲۱ تا ۰۶)</td><td>قدرتمندترین باند شبانگاهی در ایران، عبور عالی از موانع شهری</td></tr>
              <tr><td>باند ۴۱ متر</td><td>7200 - 7500 kHz</td><td>عصر، غروب و اوایل صبح</td><td>باند پرطرفدار بین‌المللی با دریافت پایدار در ساعات گرگ و میش</td></tr>
              <tr><td>باند ۳۱ متر</td><td>9400 - 9900 kHz</td><td>تمام ساعات شبانه‌روز</td><td>پایدارترین باند برای اکثر ایستگاه‌های جهان؛ نوسان اندک سیگنال</td></tr>
              <tr><td>باند ۲۵ متر</td><td>11600 - 12100 kHz</td><td>بعدازظهر تا غروب</td><td>دریافت بسیار خوب بین‌قاره‌ای در ساعات روشن روز</td></tr>
              <tr><td>باند ۱۹ متر</td><td>15100 - 15800 kHz</td><td>صبح تا اواسط بعدازظهر</td><td>انتشار شفاف روزانه در تمام فصول؛ دریافت عالی از آسیا و اروپا</td></tr>
              <tr><td>موج متوسط (MW)</td><td>531 - 1602 kHz</td><td>شب‌ها بعد از غروب آفتاب</td><td>ایستگاه‌های منطقه‌ای ارمنستان، کویت، عمان و تاجیکستان</td></tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- TAB 8: LOGS & SINPO RECEPTION TESTING -->
    <div id="tab-logs" class="tab-content">
      <div style="background: var(--bg-secondary); border: 1px solid var(--border-color); border-radius: var(--radius-lg); padding: 24px; margin-bottom: 24px;">
        <h2 style="font-size: 18px; font-weight: 800; margin-bottom: 12px; color: var(--accent);">
          📝 ثبت تجربه و آزمایش دریافت محلی (بدون ارسال به اینترنت)
        </h2>
        <p style="font-size: 13px; color: var(--text-secondary); margin-bottom: 18px;">
          یادداشت‌های آزمایش شنود شما در حافظه محلی مرورگر (Local Storage) نگهداری می‌شوند و کاملاً محرمانه هستند. می‌توانید از آنها خروجی JSON بگیرید یا نسخه‌های قبلی را بارگذاری کنید.
        </p>

        <form id="reception-log-form">
          <div class="log-form-grid">
            <div class="form-group">
              <label for="log-freq">فرکانس آزمایش‌شده (kHz):</label>
              <input type="number" id="log-freq" class="form-control" placeholder="مثلاً 5860" required>
            </div>
            <div class="form-group">
              <label for="log-station">نام شبکه یا برنامه:</label>
              <input type="text" id="log-station" class="form-control" placeholder="مثلاً رادیو فردا" required>
            </div>
            <div class="form-group">
              <label for="log-city">شهر یا منطقه تقریبی (اختیاری):</label>
              <input type="text" id="log-city" class="form-control" placeholder="مثلاً تهران، اصفهان، تبریز...">
            </div>
            <div class="form-group">
              <label for="log-receiver">نوع گیرنده / رادیو:</label>
              <input type="text" id="log-receiver" class="form-control" placeholder="مثلاً تکسان، رادیو ماشین، پاناسونیک...">
            </div>
            <div class="form-group">
              <label for="log-clarity">کیفیت و وضوح دریافت:</label>
              <select id="log-clarity" class="form-control">
                <option value="شفاف و عالی (بدون نویز)">شفاف و عالی (بدون نویز)</option>
                <option value="قابل شنیدن با نویز اندک">قابل شنیدن با نویز اندک</option>
                <option value="ضعیف ولی مفهوم">ضعیف ولی مفهوم</option>
                <option value="سیگنال بسیار ضعیف و ناخوانا">سیگنال بسیار ضعیف و ناخوانا</option>
                <option value="غیرقابل دریافت / خاموش">غیرقابل دریافت / خاموش</option>
              </select>
            </div>
            <div class="form-group">
              <label for="log-antenna">نوع آنتن:</label>
              <input type="text" id="log-antenna" class="form-control" placeholder="مثلاً تلسکوپی سرخود، سیم بیرونی...">
            </div>
          </div>
          <div class="form-group" style="margin-bottom: 16px;">
            <label for="log-notes">یادداشت و مشاهدات تکمیلی:</label>
            <textarea id="log-notes" class="form-control" rows="2" placeholder="توضیحات درباره شرایط جوی، وجود پارازیت یا تداخل..."></textarea>
          </div>
          <div style="display: flex; gap: 12px; flex-wrap: wrap;">
            <button type="submit" class="btn btn-accent">💾 ذخیره گزارش دریافت</button>
            <button type="button" class="btn" id="btn-export-logs">📤 خروجی فایل JSON لاگ‌ها</button>
            <button type="button" class="btn" id="btn-clear-logs" style="color: var(--danger);">🗑️ پاکسازی همه لاگ‌ها</button>
          </div>
        </form>
      </div>

      <div style="margin-bottom: 14px; font-weight: 700;">لاگ‌های ثبت‌شده شما:</div>
      <div class="table-container">
        <table class="data-table">
          <thead>
            <tr>
              <th>زمان ثبت (تهران)</th>
              <th>فرکانس</th>
              <th>شبکه</th>
              <th>کیفیت صدا</th>
              <th>مکان</th>
              <th>گیرنده / آنتن</th>
              <th>توضیحات</th>
            </tr>
          </thead>
          <tbody id="logs-table-body"></tbody>
        </table>
      </div>
    </div>

    <!-- TAB 9: FAVORITES -->
    <div id="tab-favorites" class="tab-content">
      <div style="margin-bottom: 16px;">
        <h2 style="font-size: 18px; font-weight: 800;">شبکه‌ها و فرکانس‌های منتخب شما</h2>
        <p style="font-size: 13px; color: var(--text-secondary);">با زدن دکمه ستاره (⭐) در کنار هر برنامه، آن را به این فهرست فوری اضافه کنید.</p>
      </div>
      <div id="favorites-grid" class="schedule-grid"></div>
    </div>

    <!-- TAB 10: UPDATE CENTER (مرکز به‌روزرسانی چندگانه) -->
    <div id="tab-update" class="tab-content">
      <div style="background: var(--bg-secondary); border: 1px solid var(--border-color); border-radius: var(--radius-lg); padding: 24px; margin-bottom: 24px;">
        <div style="display:flex; justify-content:space-between; align-items:flex-start; flex-wrap:wrap; gap:12px; margin-bottom:16px;">
          <div>
            <h2 style="font-size: 20px; font-weight: 800; color: var(--accent); margin-bottom: 4px;">
              🔄 مرکز به‌روزرسانی جامع پایگاه داده (آنلاین و آفلاین)
            </h2>
            <p style="font-size: 13.5px; color: var(--text-secondary);">
              اگر اینترنت بین‌الملل به طور موقت، با هزینه بالا یا با حجم محدود برقرار شد، با هریک از روش‌های زیر می‌توانید پایگاه داده رادیوها را فوراً به‌روز کنید.
            </p>
          </div>
          <div id="db-status-badge" style="background:var(--accent-bg); border:1px solid var(--accent); color:var(--accent); padding:6px 14px; border-radius:20px; font-size:12px; font-weight:700;">
            وضعیت داده‌ها: نسخه پیش‌فرض کارخانه
          </div>
        </div>

        <!-- CURRENT DATABASE INFO BAR -->
        <div style="background:var(--bg-card); border:1px solid var(--border-color); border-radius:var(--radius-sm); padding:12px 16px; margin-bottom:20px; font-size:13px; display:flex; flex-wrap:wrap; gap:16px; align-items:center;">
          <div>📅 <strong>فصل پخش:</strong> <span id="update-info-season">--</span></div>
          <div>🔢 <strong>تعداد شبکه‌ها:</strong> <span id="update-info-stations">--</span></div>
          <div>📡 <strong>تعداد برنامه‌ها:</strong> <span id="update-info-schedules">--</span></div>
          <div>🕒 <strong>تاریخ آخرین نگاشت داده‌ها:</strong> <span id="update-info-date">--</span></div>
        </div>

        <div id="update-status-message" style="display:none; padding:12px 16px; border-radius:var(--radius-sm); margin-bottom:20px; font-weight:700; font-size:14px;"></div>

        <!-- 5 UPDATE METHODS GRID -->
        <div class="update-grid">

          <!-- METHOD 1: DIRECT ONLINE FETCH -->
          <div class="update-card">
            <div class="update-card-title">
              <span>🌐</span> روش اول: دریافت برخط خودکار (Online)
            </div>
            <div class="update-card-desc">
              در صورت برقراری اتصال موقت به اینترنت (استارلینک، VPN، سرور اختصاصی یا آدرس گیت‌هاب)، آدرس منبع داده جدید را مشخص کرده و دکمه را بزنید.
            </div>

            <div class="form-group" style="margin-bottom:12px;">
              <label for="online-update-url">آدرس URL مخزن یا فایل JSON:</label>
              <input type="url" id="online-update-url" class="form-control" value="https://raw.githubusercontent.com/alima1000/iran-sw-radio/main/data/radio-database.json" placeholder="https://example.com/radio-database.json">
            </div>

            <div style="display:flex; align-items:center; gap:8px; margin-bottom:14px; font-size:12px; color:var(--text-secondary);">
              <input type="checkbox" id="chk-cors-proxy" checked>
              <label for="chk-cors-proxy">استفاده از پروکسی رفع محدودیت CORS (توصیه می‌شود)</label>
            </div>

            <button type="button" class="btn btn-accent" id="btn-fetch-online" style="margin-top:auto; width:100%; justify-content:center;">
              🌐 شروع دریافت برخط پایگاه داده
            </button>
          </div>

          <!-- METHOD 2: FILE UPLOAD (DRAG & DROP) -->
          <div class="update-card">
            <div class="update-card-title">
              <span>📁</span> روش دوم: بارگذاری فایل (JSON یا CSV)
            </div>
            <div class="update-card-desc">
              اگر فایل <code>radio-database.json</code> یا <code>schedules.csv</code> را از طریق تلگرام، بلوتوث یا فلش مموری از دوستی دریافت کرده‌اید، آن را انتخاب کنید.
            </div>

            <div class="drop-zone" id="file-drop-zone">
              <div style="font-size:28px; margin-bottom:6px;">📥</div>
              <div style="font-weight:700; font-size:13px; margin-bottom:4px;">فایل را اینجا رها کنید</div>
              <div style="font-size:11px; color:var(--text-secondary);">یا برای انتخاب فایل کلیک کنید (JSON یا CSV)</div>
            </div>
            <input type="file" id="file-input-updater" accept=".json,.csv" style="display:none;">

            <div style="font-size:11px; color:var(--text-muted); margin-top:auto;">
              ✓ پردازش ۱۰۰٪ محلی در مرورگر شما بدون ارسال به هیچ سروری
            </div>
          </div>

          <!-- METHOD 3: PASTE RAW JSON -->
          <div class="update-card">
            <div class="update-card-title">
              <span>📋</span> روش سوم: ورود مستقیم متن یا کد JSON
            </div>
            <div class="update-card-desc">
              مناسب اینترنت‌های با پهنای باند بسیار ضعیف (پیام‌رسان‌های متنی یا SMS کدگذاری‌شده). متن کد JSON را در کادر زیر جای‌گذاری (Paste) کنید:
            </div>

            <textarea id="paste-json-input" class="form-control" rows="3" placeholder="کد JSON پایگاه داده جدید را در اینجا Paste کنید..."></textarea>

            <button type="button" class="btn btn-accent" id="btn-apply-pasted-json" style="margin-top:12px; width:100%; justify-content:center;">
              ✓ بررسی و اعمال داده‌های متنی
            </button>
          </div>

          <!-- METHOD 4: EXPORT PERMANENT UPDATED HTML -->
          <div class="update-card" style="border:1px solid var(--success);">
            <div class="update-card-title" style="color:var(--success);">
              <span>💾</span> روش چهارم: تولید و ذخیره HTML جدید
            </div>
            <div class="update-card-desc">
              پس از هرگونه به‌روزرسانی (آنلاین، فایل یا متن)، با این گزینه یک فایل HTML مستقل جدید دانلود کنید که تمام داده‌های جدید در آن ذخیره شده و برای استفاده دائم روی فلش مموری یا گوشی‌های دیگر آماده است.
            </div>

            <button type="button" class="btn btn-success" id="btn-export-updated-html" style="margin-top:auto; width:100%; justify-content:center;">
              📥 دانلود فایل HTML مستقل به‌روزشده
            </button>
          </div>

        </div>

        <!-- FACTORY RESET & CLI INSTRUCTIONS -->
        <div style="border-top:1px solid var(--border-color); padding-top:18px; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px;">
          <div>
            <div style="font-weight:700; font-size:13px; color:var(--text-primary); margin-bottom:2px;">بازگشت به تنظیمات اولیه کارخانه:</div>
            <div style="font-size:12px; color:var(--text-secondary);">در صورت بروز هرگونه مشکل در داده‌های واردشده، می‌توانید پایگاه داده اصلی برنامه را بازگردانید.</div>
          </div>
          <button type="button" class="btn" id="btn-factory-reset" style="color:var(--danger); border-color:var(--danger);">
            🗑️ بازنشانی به داده‌های پیش‌فرض کارخانه
          </button>
        </div>

      </div>
    </div>

  </main>

  <!-- STATION DETAIL MODAL -->
  <div class="modal-overlay" id="station-modal">
    <div class="modal-card">
      <button class="modal-close" onclick="closeModal()">&times;</button>
      <div id="modal-body-content"></div>
    </div>
  </div>

  <!-- EMBEDDED DATABASE JSON (OFFLINE PERSISTENCE) -->
  <script id="embedded-database" type="application/json">
__EMBEDDED_DB_JSON__
  </script>

  <!-- JAVASCRIPT APPLICATION LOGIC -->
  <script>
    /* -------------------------------------------------------------
       STANDALONE JAVASCRIPT APPLICATION CORE & HYBRID UPDATER
       ------------------------------------------------------------- */
    
    // Check if an updated database exists in localStorage
    const BUILTIN_DB = JSON.parse(document.getElementById('embedded-database').textContent);
    let CUSTOM_DB = null;
    try {
      const saved = localStorage.getItem('iran_sw_custom_db');
      if (saved) {
        CUSTOM_DB = JSON.parse(saved);
      }
    } catch (e) {
      console.warn('Could not read custom DB from localStorage', e);
    }

    let DB = CUSTOM_DB || BUILTIN_DB;
    let FAVORITES = JSON.parse(localStorage.getItem('iran_sw_favorites') || '[]');
    let RECEPTION_LOGS = JSON.parse(localStorage.getItem('iran_sw_logs') || '[]');
    let IS_EMERGENCY = false;
    let CURRENT_HOUR_PLANNER = 18; // Default 18:00 Tehran

    // Persian Character Normalization Helper
    function normalizePersianText(str) {
      if (!str) return '';
      return String(str)
        .replace(/[ي]/g, 'ی')
        .replace(/[ك]/g, 'ک')
        .replace(/[آأإ]/g, 'ا')
        .replace(/[\\u200B-\\u200D\\uFEFF]/g, '')
        .replace(/[\\s\\-_]+/g, ' ')
        .toLowerCase()
        .trim();
    }

    // Strict Tehran Time Calculator (UTC+03:30, Iran has NO DST since 2022)
    function getTehranDate() {
      const now = new Date();
      const utcMs = now.getTime() + (now.getTimezoneOffset() * 60000);
      const tehranMs = utcMs + (210 * 60000);
      return new Date(tehranMs);
    }

    function updateTehranClock() {
      const t = getTehranDate();
      const h = String(t.getHours()).padStart(2, '0');
      const m = String(t.getMinutes()).padStart(2, '0');
      const s = String(t.getSeconds()).padStart(2, '0');
      const timeStr = h + ':' + m + ':' + s;
      
      const clockEl = document.getElementById('tehran-time-display');
      if (clockEl) clockEl.textContent = timeStr;

      const dateEl = document.getElementById('tehran-date-display');
      if (dateEl) {
        const y = t.getFullYear();
        const mon = String(t.getMonth() + 1).padStart(2, '0');
        const d = String(t.getDate()).padStart(2, '0');
        dateEl.textContent = y + '/' + mon + '/' + d + ' • به وقت رسمی تهران';
      }

      const nowInd = document.getElementById('now-time-indicator');
      if (nowInd) nowInd.textContent = h + ':' + m;
    }
    setInterval(updateTehranClock, 1000);
    updateTehranClock();

    // Check if schedule is currently active at target time (HH:MM string)
    function isScheduleActiveAtTime(sch, targetHHMM) {
      const partsT = targetHHMM.split(':').map(Number);
      const targetMins = partsT[0] * 60 + partsT[1];

      const partsS = sch.time_start_tehran.split(':').map(Number);
      const startMins = partsS[0] * 60 + partsS[1];

      const partsE = sch.time_end_tehran.split(':').map(Number);
      const endMins = partsE[0] * 60 + partsE[1];

      if (sch.duration_minutes >= 1440) return true; // 24h broadcast

      if (endMins > startMins) {
        return targetMins >= startMins && targetMins < endMins;
      } else {
        return targetMins >= startMins || targetMins < endMins;
      }
    }

    // Toggle Favorites
    function toggleFavorite(id) {
      if (FAVORITES.includes(id)) {
        FAVORITES = FAVORITES.filter(x => x !== id);
      } else {
        FAVORITES.push(id);
      }
      localStorage.setItem('iran_sw_favorites', JSON.stringify(FAVORITES));
      updateFavCount();
      renderAll();
    }

    function updateFavCount() {
      const el = document.getElementById('fav-count');
      if (el) el.textContent = FAVORITES.length;
    }

    // Filter and Sort Engine
    function filterSchedules(list) {
      const search = normalizePersianText(document.getElementById('global-search-input').value);
      const langFilter = document.getElementById('filter-language').value;
      const catFilter = document.getElementById('filter-category').value;
      const bandFilter = document.getElementById('filter-band').value;
      const confFilter = document.getElementById('filter-confidence').value;
      const sortVal = document.getElementById('filter-sort').value;

      let res = list.filter(item => {
        if (IS_EMERGENCY) {
          if (!['fa', 'dr', 'tj'].includes(item.language)) return false;
          if (item.category !== 'news' && item.category !== 'general') return false;
        }

        if (langFilter === 'farsi' && !['fa', 'dr', 'tj'].includes(item.language)) return false;
        if (langFilter === 'en' && item.language !== 'en') return false;
        if (langFilter === 'ar' && item.language !== 'ar') return false;
        if (langFilter === 'other' && ['fa', 'dr', 'tj', 'en', 'ar'].includes(item.language)) return false;

        if (catFilter !== 'all' && item.category !== catFilter) return false;
        if (bandFilter !== 'all' && item.band_code !== bandFilter) return false;

        if (confFilter === 'verified' && !['A', 'B'].includes(item.confidence_level)) return false;
        if (confFilter === 'review' && !['C', 'D'].includes(item.confidence_level)) return false;

        if (search) {
          const hay = normalizePersianText(
            item.station_name_fa + ' ' + item.station_name_en + ' ' + item.program_title + ' ' + item.frequency_khz + ' ' + item.language_fa + ' ' + item.transmitter_site + ' ' + item.category_fa + ' ' + item.notes
          );
          if (!hay.includes(search)) return false;
        }

        return true;
      });

      res.sort((a, b) => {
        if (sortVal === 'time-asc') return a.time_start_tehran.localeCompare(b.time_start_tehran);
        if (sortVal === 'freq-asc') return a.frequency_khz - b.frequency_khz;
        if (sortVal === 'freq-desc') return b.frequency_khz - a.frequency_khz;
        if (sortVal === 'name-asc') return a.station_name_fa.localeCompare(b.station_name_fa);
        if (sortVal === 'conf-desc') return a.confidence_level.localeCompare(b.confidence_level);
        return 0;
      });

      return res;
    }

    // Render HTML card for a schedule
    function createScheduleCard(sch) {
      const isFav = FAVORITES.includes(sch.id);
      const altsHtml = sch.alternative_frequencies && sch.alternative_frequencies.length
        ? '<div class="alts-tag-box">فرکانس‌های جایگزین: ' +
            sch.alternative_frequencies.map(f => '<span class="alts-pill" onclick="filterByFrequency(' + f + ')">' + f + ' kHz</span>').join('') +
          '</div>'
        : '';

      return `
        <div class="schedule-card" id="card-` + sch.id + `">
          <div class="card-top">
            <div>
              <span class="freq-badge">` + sch.frequency_khz + ` <small style="font-size:12px">kHz</small></span>
              <span class="band-pill">` + sch.band_name_fa + `</span>
            </div>
            <div style="display:flex; align-items:center; gap:8px;">
              <span class="badge-conf badge-conf-` + sch.confidence_level + `">سطح ` + sch.confidence_level + `</span>
              <button class="star-btn ` + (isFav ? 'starred' : '') + `" onclick="toggleFavorite('` + sch.id + `')" title="افزودن به علاقه‌مندی‌ها">★</button>
            </div>
          </div>

          <div class="station-name">` + sch.station_name_fa + `</div>
          <div class="program-title">` + sch.program_title + `</div>

          <div class="card-meta-list">
            <div class="meta-row">
              <span class="meta-label">⏰ زمان پخش (تهران):</span>
              <span class="meta-value" style="color: var(--accent);">` + sch.time_display_tehran + `</span>
            </div>
            <div class="meta-row">
              <span class="meta-label">🌍 زمان جهانی (UTC):</span>
              <span class="meta-value">` + sch.time_start_utc + ` تا ` + sch.time_end_utc + `</span>
            </div>
            <div class="meta-row">
              <span class="meta-label">🗣️ زبان و دسته‌بندی:</span>
              <span class="meta-value">` + sch.language_fa + ` • ` + sch.category_fa + `</span>
            </div>
            <div class="meta-row">
              <span class="meta-label">📡 فرستنده / توان:</span>
              <span class="meta-value">` + sch.transmitter_site + ` (` + (sch.transmitter_power_kw || '؟') + ` kW)</span>
            </div>
            <div class="meta-row">
              <span class="meta-label">📌 وضعیت اعتبار:</span>
              <span class="meta-value" style="font-size: 11px;">` + sch.status_fa + `</span>
            </div>
          </div>

          ` + altsHtml + `

          <div class="card-footer">
            <small style="color: var(--text-muted); font-size:11px;">فصل: ` + sch.season + `</small>
            <button class="btn" style="padding: 4px 8px; font-size: 11px;" onclick="openStationModal('` + sch.station_id + `')">
              جزئیات شبکه
            </button>
          </div>
        </div>
      `;
    }

    window.filterByFrequency = function(khz) {
      document.getElementById('global-search-input').value = String(khz);
      switchTab('tab-all');
      renderAll();
    };

    function renderNowOnAir() {
      const customVal = document.getElementById('custom-time-picker').value;
      let targetTime;
      if (customVal) {
        targetTime = customVal;
      } else {
        const t = getTehranDate();
        targetTime = String(t.getHours()).padStart(2, '0') + ':' + String(t.getMinutes()).padStart(2, '0');
      }

      const activeSchedules = DB.schedules.filter(s => isScheduleActiveAtTime(s, targetTime));
      const filtered = filterSchedules(activeSchedules);
      const container = document.getElementById('now-on-air-grid');

      if (!filtered.length) {
        container.innerHTML = `
          <div style="grid-column: 1 / -1; text-align: center; padding: 40px; background: var(--bg-secondary); border-radius: var(--radius-md); border: 1px dashed var(--border-color);">
            <div style="font-size: 32px; margin-bottom: 10px;">📻</div>
            <div style="font-size: 16px; font-weight: 700; color: var(--text-primary); margin-bottom: 6px;">در این ساعت هیچ برنامه‌ای طبق فیلترهای انتخابی در حال پخش نیست</div>
            <p style="font-size: 13px; color: var(--text-secondary);">فیلتر زبان یا دسته‌بندی را تغییر دهید یا به بخش «نمای ۲۴ ساعته» مراجعه کنید.</p>
          </div>
        `;
        return;
      }
      container.innerHTML = filtered.map(createScheduleCard).join('');
    }

    function renderAllSchedules() {
      const filtered = filterSchedules(DB.schedules);
      const container = document.getElementById('all-schedules-grid');
      const countEl = document.getElementById('all-count-display');
      if (countEl) countEl.textContent = 'نمایش ' + filtered.length + ' از ' + DB.schedules.length + ' برنامه';

      if (!filtered.length) {
        container.innerHTML = `
          <div style="grid-column: 1 / -1; text-align: center; padding: 40px; background: var(--bg-secondary); border-radius: var(--radius-md);">
            هیچ برنامه‌ای با مشخصات جستوجوشده یافت نشد. دکمه «پاکسازی فیلترها» را بزنید.
          </div>
        `;
        return;
      }
      container.innerHTML = filtered.map(createScheduleCard).join('');
    }

    function initHourSelector() {
      const container = document.getElementById('hour-selector-container');
      container.innerHTML = '';
      for (let h = 0; h < 24; h++) {
        const strH = String(h).padStart(2, '0');
        const btn = document.createElement('button');
        btn.className = 'hour-btn ' + (h === CURRENT_HOUR_PLANNER ? 'active' : '');
        btn.textContent = strH + ':۰۰';
        btn.onclick = () => {
          CURRENT_HOUR_PLANNER = h;
          initHourSelector();
          renderPlanner();
        };
        container.appendChild(btn);
      }
    }

    function renderPlanner() {
      const targetTime = String(CURRENT_HOUR_PLANNER).padStart(2, '0') + ':00';
      const headerEl = document.getElementById('planner-hour-header');
      if (headerEl) headerEl.textContent = 'برنامه‌های فعال در ساعت ' + targetTime + ' تا ' + String((CURRENT_HOUR_PLANNER+1)%24).padStart(2, '0') + ':00 تهران:';

      const activeSchedules = DB.schedules.filter(s => isScheduleActiveAtTime(s, targetTime));
      const filtered = filterSchedules(activeSchedules);
      const container = document.getElementById('planner-schedules-grid');

      if (!filtered.length) {
        container.innerHTML = `<div style="grid-column: 1 / -1; text-align: center; padding: 30px; background: var(--bg-secondary); border-radius: var(--radius-md);">برنامه‌ای در این ساعت برای فیلترهای کنونی ثبت نشده است.</div>`;
        return;
      }
      container.innerHTML = filtered.map(createScheduleCard).join('');
    }

    function renderHourlyMatrix() {
      const container = document.getElementById('hourly-matrix-container');
      let html = '';

      for (let h = 0; h < 24; h++) {
        const timeSlotStr = String(h).padStart(2, '0') + ':00 تا ' + String((h+1)%24).padStart(2, '0') + ':00';
        const testTime = String(h).padStart(2, '0') + ':15';
        const slotSchedules = DB.schedules.filter(s => isScheduleActiveAtTime(s, testTime));

        if (!slotSchedules.length) continue;

        html += `
          <div style="background: var(--bg-secondary); border: 1px solid var(--border-color); border-radius: var(--radius-md); margin-bottom: 14px; overflow: hidden;">
            <div style="background: var(--bg-card); padding: 10px 16px; font-weight: 800; font-size: 15px; color: var(--accent); display: flex; justify-content: space-between;">
              <span>⏰ ` + timeSlotStr + ` به وقت تهران</span>
              <span style="font-size: 12px; color: var(--text-secondary);">` + slotSchedules.length + ` فرکانس فعال</span>
            </div>
            <div style="padding: 12px 16px;">
              <table class="data-table">
                <thead>
                  <tr>
                    <th>فرکانس</th>
                    <th>باند</th>
                    <th>شبکه و برنامه</th>
                    <th>زبان</th>
                    <th>فرستنده</th>
                    <th>اعتبار</th>
                  </tr>
                </thead>
                <tbody>
                  ` + slotSchedules.map(s => `
                    <tr>
                      <td><strong style="color:var(--accent); font-size:15px;">` + s.frequency_khz + ` kHz</strong></td>
                      <td>` + s.band_name_fa + `</td>
                      <td><strong>` + s.station_name_fa + `</strong> <br><small style="color:var(--text-secondary);">` + s.program_title + `</small></td>
                      <td>` + s.language_fa + `</td>
                      <td>` + s.transmitter_site + `</td>
                      <td><span class="badge-conf badge-conf-` + s.confidence_level + `">سطح ` + s.confidence_level + `</span></td>
                    </tr>
                  `).join('') + `
                </tbody>
              </table>
            </div>
          </div>
        `;
      }
      container.innerHTML = html;
    }

    function renderFreqTable() {
      const sorted = [...DB.schedules].sort((a, b) => a.frequency_khz - b.frequency_khz);
      const filtered = filterSchedules(sorted);
      const tbody = document.getElementById('freq-table-body');

      tbody.innerHTML = filtered.map(s => `
        <tr>
          <td><strong style="font-size: 16px; color: var(--accent);">` + s.frequency_khz + `</strong> <small>kHz</small></td>
          <td><span class="band-pill">` + s.band_name_fa + `</span></td>
          <td><strong>` + s.station_name_fa + `</strong><br><small style="color:var(--text-secondary);">` + s.program_title + `</small></td>
          <td>` + s.language_fa + `</td>
          <td><span style="color:var(--accent); font-weight:700;">` + s.time_display_tehran + `</span></td>
          <td>` + s.transmitter_site + ` (` + (s.transmitter_power_kw || '؟') + ` kW)</td>
          <td><span class="badge-conf badge-conf-` + s.confidence_level + `">سطح ` + s.confidence_level + `</span></td>
          <td>
            <button class="btn" style="padding:4px 8px; font-size:11px;" onclick="openStationModal('` + s.station_id + `')">مشاهده</button>
          </td>
        </tr>
      `).join('');
    }

    function renderStations() {
      const container = document.getElementById('stations-grid');
      container.innerHTML = DB.stations.map(stn => {
        const freqs = DB.schedules.filter(s => s.station_id === stn.station_id);
        const uniqueFreqs = [...new Set(freqs.map(s => s.frequency_khz))].sort((a,b)=>a-b);
        const isHist = stn.sw_status === 'inactive_historical';

        return `
          <div class="schedule-card" style="` + (isHist ? 'opacity: 0.8; border-style: dashed;' : '') + `">
            <div class="card-top">
              <div>
                <div class="station-name" style="font-size: 18px;">` + stn.name_fa + `</div>
                <div style="font-size: 12px; color: var(--text-secondary);">` + stn.name_en + ` • ` + stn.country_fa + `</div>
              </div>
              <span class="badge-conf badge-conf-${stn.confidence_level}">سطح ` + stn.confidence_level + `</span>
            </div>

            <p style="font-size: 13px; color: var(--text-primary); margin: 10px 0; line-height: 1.8;">
              ` + stn.description_fa + `
            </p>

            <div class="card-meta-list">
              <div class="meta-row">
                <span class="meta-label">وضعیت موج کوتاه:</span>
                <span class="meta-value" style="color: ` + (isHist ? 'var(--danger)' : 'var(--success)') + `;">` + stn.sw_status_fa + `</span>
              </div>
              <div class="meta-row">
                <span class="meta-label">فرستنده‌های اصلی:</span>
                <span class="meta-value">` + stn.primary_transmitters_fa + `</span>
              </div>
              <div class="meta-row">
                <span class="meta-label">فرکانس‌های ثبت‌شده:</span>
                <span class="meta-value">` + (uniqueFreqs.length ? uniqueFreqs.map(f => f + ' kHz').join('، ') : 'ندارد') + `</span>
              </div>
            </div>

            <div class="card-footer">
              <small style="color: var(--text-muted); font-size:11px;">سازمان: ` + stn.broadcaster + `</small>
              <button class="btn btn-accent" style="padding: 4px 10px; font-size: 11px;" onclick="openStationModal('` + stn.station_id + `')">
                مشاهده جدول کامل
              </button>
            </div>
          </div>
        `;
      }).join('');
    }

    function renderFavorites() {
      const favSchedules = DB.schedules.filter(s => FAVORITES.includes(s.id));
      const container = document.getElementById('favorites-grid');

      if (!favSchedules.length) {
        container.innerHTML = `
          <div style="grid-column: 1 / -1; text-align: center; padding: 40px; background: var(--bg-secondary); border-radius: var(--radius-md);">
            <div style="font-size: 32px; margin-bottom: 8px;">⭐</div>
            <div style="font-weight: 700; margin-bottom: 6px;">هنوز برنامه‌ای به علاقه‌مندی‌ها اضافه نشده است</div>
            <p style="font-size: 13px; color: var(--text-secondary);">با زدن ستاره در گوشه هر کارت، فرکانس‌های مورد نیاز خود را برای دسترسی سریع ذخیره کنید.</p>
          </div>
        `;
        return;
      }
      container.innerHTML = favSchedules.map(createScheduleCard).join('');
    }

    window.openStationModal = function(stnId) {
      const stn = DB.stations.find(s => s.station_id === stnId);
      if (!stn) return;
      const stnSchedules = DB.schedules.filter(s => s.station_id === stnId);

      const modalBody = document.getElementById('modal-body-content');
      modalBody.innerHTML = `
        <div style="margin-bottom: 16px;">
          <h2 style="font-size: 20px; font-weight: 800; color: var(--text-primary);">` + stn.name_fa + `</h2>
          <div style="font-size: 13px; color: var(--text-secondary);">` + stn.name_en + ` • ` + stn.country_fa + ` • ` + stn.broadcaster + `</div>
        </div>

        <div style="background: var(--bg-card); padding: 14px; border-radius: var(--radius-sm); margin-bottom: 18px; font-size: 13px; line-height: 1.8;">
          ` + stn.description_fa + `
        </div>

        <div style="margin-bottom: 14px; font-weight: 700;">جدول فرکانس‌ها و ساعات پخش به وقت تهران:</div>
        <div class="table-container" style="margin-bottom: 18px;">
          <table class="data-table">
            <thead>
              <tr>
                <th>فرکانس</th>
                <th>باند</th>
                <th>ساعت تهران</th>
                <th>برنامه</th>
                <th>فرستنده</th>
                <th>اعتبار</th>
              </tr>
            </thead>
            <tbody>
              ` + stnSchedules.map(s => `
                <tr>
                  <td><strong style="color:var(--accent);">` + s.frequency_khz + ` kHz</strong></td>
                  <td>` + s.band_name_fa + `</td>
                  <td><strong style="color:var(--accent);">` + s.time_display_tehran + `</strong></td>
                  <td>` + s.program_title + `</td>
                  <td>` + s.transmitter_site + `</td>
                  <td><span class="badge-conf badge-conf-` + s.confidence_level + `">سطح ` + s.confidence_level + `</span></td>
                </tr>
              `).join('') + `
            </tbody>
          </table>
        </div>

        <div style="font-size: 12px; color: var(--text-secondary); border-top: 1px solid var(--border-color); padding-top: 10px;">
          <strong>توضیحات سطح اعتبار:</strong> ` + stn.confidence_description_fa + `
        </div>
      `;

      document.getElementById('station-modal').classList.add('open');
    };

    window.closeModal = function() {
      document.getElementById('station-modal').classList.remove('open');
    };

    function renderLogsTable() {
      const tbody = document.getElementById('logs-table-body');
      if (!RECEPTION_LOGS.length) {
        tbody.innerHTML = '<tr><td colspan="7" style="text-align:center; padding:20px; color:var(--text-muted);">هنوز هیچ آزمایشی ثبت نشده است. از فرم بالا استفاده کنید.</td></tr>';
        return;
      }
      tbody.innerHTML = RECEPTION_LOGS.map(log => `
        <tr>
          <td>` + log.time_tehran + `</td>
          <td><strong>` + log.freq + ` kHz</strong></td>
          <td>` + log.station + `</td>
          <td><span style="color:var(--success); font-weight:700;">` + log.clarity + `</span></td>
          <td>` + (log.city || '-') + `</td>
          <td>` + (log.receiver || '-') + ` / ` + (log.antenna || '-') + `</td>
          <td>` + (log.notes || '-') + `</td>
        </tr>
      `).join('');
    }

    document.getElementById('reception-log-form').addEventListener('submit', function(e) {
      e.preventDefault();
      const t = getTehranDate();
      const nowStr = t.getFullYear() + '/' + String(t.getMonth()+1).padStart(2,'0') + '/' + String(t.getDate()).padStart(2,'0') + ' ' + String(t.getHours()).padStart(2,'0') + ':' + String(t.getMinutes()).padStart(2,'0');

      const newLog = {
        id: 'LOG-' + Date.now(),
        time_tehran: nowStr,
        freq: document.getElementById('log-freq').value,
        station: document.getElementById('log-station').value,
        city: document.getElementById('log-city').value,
        receiver: document.getElementById('log-receiver').value,
        clarity: document.getElementById('log-clarity').value,
        antenna: document.getElementById('log-antenna').value,
        notes: document.getElementById('log-notes').value
      };

      RECEPTION_LOGS.unshift(newLog);
      localStorage.setItem('iran_sw_logs', JSON.stringify(RECEPTION_LOGS));
      this.reset();
      renderLogsTable();
      alert('گزارش آزمایش با موفقیت در حافظه محلی ذخیره شد.');
    });

    document.getElementById('btn-export-logs').addEventListener('click', function() {
      const blob = new Blob([JSON.stringify(RECEPTION_LOGS, null, 2)], {type: 'application/json'});
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'Iran-SW-Reception-Logs-' + Date.now() + '.json';
      a.click();
    });

    document.getElementById('btn-clear-logs').addEventListener('click', function() {
      if (confirm('آیا از پاک کردن تمام لاگ‌های ثبت‌شده مطمئن هستید؟')) {
        RECEPTION_LOGS = [];
        localStorage.removeItem('iran_sw_logs');
        renderLogsTable();
      }
    });

    /* -------------------------------------------------------------
       DATABASE UPDATE CENTER ENGINE
       ------------------------------------------------------------- */
    function showUpdateMessage(text, isError) {
      const el = document.getElementById('update-status-message');
      el.style.display = 'block';
      el.style.background = isError ? 'var(--danger-bg)' : 'var(--success-bg)';
      el.style.color = isError ? 'var(--danger)' : 'var(--success)';
      el.style.border = '1px solid ' + (isError ? 'var(--danger)' : 'var(--success)');
      el.textContent = text;
      setTimeout(() => {
        el.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
      }, 100);
    }

    function applyNewDatabase(newDb, sourceDescription) {
      if (!newDb || !newDb.schedules || !Array.isArray(newDb.schedules) || newDb.schedules.length === 0) {
        showUpdateMessage('خطا: ساختار داده‌های دریافتی نامعتبر است (رکوردهای schedules یافت نشد).', true);
        return false;
      }

      // Check stations
      if (!newDb.stations || !Array.isArray(newDb.stations)) {
        newDb.stations = DB.stations; // Fallback to current
      }

      // Update metadata timestamp
      if (!newDb.metadata) newDb.metadata = {};
      const t = getTehranDate();
      newDb.metadata.last_client_update = t.getFullYear() + '/' + String(t.getMonth()+1).padStart(2,'0') + '/' + String(t.getDate()).padStart(2,'0') + ' ' + String(t.getHours()).padStart(2,'0') + ':' + String(t.getMinutes()).padStart(2,'0');
      newDb.metadata.update_source_note = sourceDescription;

      // Save to localStorage
      try {
        localStorage.setItem('iran_sw_custom_db', JSON.stringify(newDb));
      } catch (err) {
        console.warn('LocalStorage quota or permission error:', err);
      }

      DB = newDb;
      CUSTOM_DB = newDb;

      showUpdateMessage('✓ پایگاه داده با موفقیت از ' + sourceDescription + ' به‌روزرسانی شد. تعداد ' + DB.schedules.length + ' برنامه فعال بارگذاری گردید.', false);
      renderAll();
      return true;
    }

    // Method 1: Fetch Online
    document.getElementById('btn-fetch-online').addEventListener('click', async function() {
      const urlInput = document.getElementById('online-update-url').value.trim();
      const useProxy = document.getElementById('chk-cors-proxy').checked;

      if (!urlInput) {
        showUpdateMessage('لطفاً آدرس اینترنتی معتبر وارد کنید.', true);
        return;
      }

      const btn = this;
      const originalText = btn.innerHTML;
      btn.innerHTML = '⏳ در حال برقراری ارتباط با اینترنت و دریافت داده...';
      btn.disabled = true;

      let finalUrl = urlInput;
      if (useProxy) {
        finalUrl = 'https://api.allorigins.win/raw?url=' + encodeURIComponent(urlInput);
      }

      try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 18000); // 18s timeout

        const response = await fetch(finalUrl, { signal: controller.signal });
        clearTimeout(timeoutId);

        if (!response.ok) {
          throw new Error('کد خطای HTTP: ' + response.status);
        }

        const data = await response.json();
        applyNewDatabase(data, 'آدرس اینترنتی آنلاین (' + urlInput + ')');
      } catch (err) {
        console.error('Online update failed:', err);
        showUpdateMessage('❌ خطا در دریافت آنلاین: ' + err.message + '. در صورت قطعی اینترنت، از روش‌های «بارگذاری فایل» یا «ورود متن» استفاده نمایید.', true);
      } finally {
        btn.innerHTML = originalText;
        btn.disabled = false;
      }
    });

    // Method 2: File Upload
    const dropZone = document.getElementById('file-drop-zone');
    const fileInput = document.getElementById('file-input-updater');

    dropZone.addEventListener('click', () => fileInput.click());
    dropZone.addEventListener('dragover', (e) => {
      e.preventDefault();
      dropZone.style.background = 'rgba(56, 139, 253, 0.35)';
    });
    dropZone.addEventListener('dragleave', () => {
      dropZone.style.background = 'var(--accent-bg)';
    });
    dropZone.addEventListener('drop', (e) => {
      e.preventDefault();
      dropZone.style.background = 'var(--accent-bg)';
      if (e.dataTransfer.files.length) {
        handleFileImport(e.dataTransfer.files[0]);
      }
    });
    fileInput.addEventListener('change', () => {
      if (fileInput.files.length) {
        handleFileImport(fileInput.files[0]);
      }
    });

    function handleFileImport(file) {
      const reader = new FileReader();
      reader.onload = function(e) {
        const text = e.target.result;
        try {
          if (file.name.endsWith('.json') || text.trim().startsWith('{')) {
            const data = JSON.parse(text);
            applyNewDatabase(data, 'فایل محلی (' + file.name + ')');
          } else if (file.name.endsWith('.csv')) {
            showUpdateMessage('فایل CSV شناسایی شد. لطفاً فایل جامع radio-database.json را وارد کنید یا از اسکریپت tools استفاده نمایید.', true);
          } else {
            showUpdateMessage('فرمت فایل پشتیبانی نمی‌شود. لطفاً فایل JSON وارد کنید.', true);
          }
        } catch (err) {
          showUpdateMessage('خطا در خواندن فایل: ' + err.message, true);
        }
      };
      reader.readAsText(file, 'utf-8');
    }

    // Method 3: Paste Raw JSON
    document.getElementById('btn-apply-pasted-json').addEventListener('click', function() {
      const text = document.getElementById('paste-json-input').value.trim();
      if (!text) {
        showUpdateMessage('لطفاً ابتدا کد JSON را در کادر متنی جای‌گذاری کنید.', true);
        return;
      }
      try {
        const data = JSON.parse(text);
        applyNewDatabase(data, 'متن واردشده دستی');
        document.getElementById('paste-json-input').value = '';
      } catch (err) {
        showUpdateMessage('خطا در تجزیه متن JSON: ' + err.message, true);
      }
    });

    // Method 4: Export Permanent Updated HTML
    document.getElementById('btn-export-updated-html').addEventListener('click', function() {
      try {
        let fullHtml = document.documentElement.outerHTML;
        // Inject current DB into the script tag
        const dbString = JSON.stringify(DB, null, 2);
        const scriptStartTag = '<script id="embedded-database" type="application/json">';
        const scriptEndTag = '<\\/script>';
        
        // Replace inner JSON of embedded-database script
        const pattern = new RegExp('(<script id="embedded-database" type="application\\/json">)[\\s\\S]*?(<\\/script>)');
        fullHtml = fullHtml.replace(pattern, '$1\\n' + dbString + '\\n$2');

        const blob = new Blob([fullHtml], { type: 'text/html;charset=utf-8' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'Iran-SW-Radio-Guide.html';
        a.click();
        showUpdateMessage('✓ فایل جدید Iran-SW-Radio-Guide.html با داده‌های به‌روزشده با موفقیت ذخیره شد.', false);
      } catch (err) {
        showUpdateMessage('خطا در ساخت فایل HTML: ' + err.message, true);
      }
    });

    // Method 5: Factory Reset
    document.getElementById('btn-factory-reset').addEventListener('click', function() {
      if (confirm('آیا مطمئن هستید که می‌خواهید تمام به‌روزرسانی‌های واردشده را پاک کرده و به نسخه کارخانه بازگردید؟')) {
        localStorage.removeItem('iran_sw_custom_db');
        CUSTOM_DB = null;
        DB = BUILTIN_DB;
        showUpdateMessage('✓ پایگاه داده به نسخه اولیه و پیش‌فرض کارخانه بازنشانی شد.', false);
        renderAll();
      }
    });

    // Update Status Indicators in Header & Update Tab
    function updateDatabaseStatusIndicators() {
      const isCustom = !!CUSTOM_DB;
      const statusBadge = document.getElementById('db-status-badge');
      if (statusBadge) {
        if (isCustom) {
          statusBadge.textContent = 'وضعیت: نسخه سفارشی به‌روزشده';
          statusBadge.style.background = 'var(--success-bg)';
          statusBadge.style.color = 'var(--success)';
          statusBadge.style.borderColor = 'var(--success)';
        } else {
          statusBadge.textContent = 'وضعیت: نسخه پیش‌فرض کارخانه (B26)';
          statusBadge.style.background = 'var(--accent-bg)';
          statusBadge.style.color = 'var(--accent)';
          statusBadge.style.borderColor = 'var(--accent)';
        }
      }

      const seasonEl = document.getElementById('update-info-season');
      const stnEl = document.getElementById('update-info-stations');
      const schEl = document.getElementById('update-info-schedules');
      const dateEl = document.getElementById('update-info-date');

      if (seasonEl) seasonEl.textContent = (DB.metadata && DB.metadata.season) || 'B26 جاری';
      if (stnEl) stnEl.textContent = DB.stations.length;
      if (schEl) schEl.textContent = DB.schedules.length;
      if (dateEl) {
        dateEl.textContent = (DB.metadata && (DB.metadata.last_client_update || DB.metadata.last_database_update)) || '2026-10-28';
      }

      // Also update top stat cards
      const farsiCount = DB.schedules.filter(s => ['fa', 'dr', 'tj'].includes(s.language)).length;
      const verifiedCount = DB.schedules.filter(s => ['A', 'B'].includes(s.confidence_level)).length;
      const reviewCount = DB.schedules.filter(s => ['C', 'D'].includes(s.confidence_level)).length;

      const statStn = document.getElementById('stat-stations');
      const statSch = document.getElementById('stat-schedules');
      const statFar = document.getElementById('stat-farsi');
      const statVer = document.getElementById('stat-verified');
      const statRev = document.getElementById('stat-review');
      const tabAllCount = document.getElementById('tab-all-count');

      if (statStn) statStn.textContent = DB.stations.length;
      if (statSch) statSch.textContent = DB.schedules.length;
      if (statFar) statFar.textContent = farsiCount;
      if (statVer) statVer.textContent = verifiedCount;
      if (statRev) statRev.textContent = reviewCount;
      if (tabAllCount) tabAllCount.textContent = DB.schedules.length;
    }

    // Master Render All
    function renderAll() {
      renderNowOnAir();
      renderAllSchedules();
      renderPlanner();
      renderHourlyMatrix();
      renderFreqTable();
      renderStations();
      renderFavorites();
      renderLogsTable();
      updateFavCount();
      updateDatabaseStatusIndicators();
    }

    // Tab Navigation
    window.switchTab = function(tabId) {
      document.querySelectorAll('.nav-tab').forEach(t => t.classList.remove('active'));
      document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
      const activeBtn = document.querySelector('.nav-tab[data-tab="' + tabId + '"]');
      const activeContent = document.getElementById(tabId);
      if (activeBtn) activeBtn.classList.add('active');
      if (activeContent) activeContent.classList.add('active');
      window.scrollTo({ top: 0, behavior: 'smooth' });
    };

    document.querySelectorAll('.nav-tab').forEach(tab => {
      tab.addEventListener('click', () => switchTab(tab.getAttribute('data-tab')));
    });

    // Filter Listeners
    ['global-search-input', 'filter-language', 'filter-category', 'filter-band', 'filter-confidence', 'filter-sort'].forEach(id => {
      const el = document.getElementById(id);
      if (el) el.addEventListener('input', renderAll);
    });

    document.getElementById('custom-time-picker').addEventListener('input', renderNowOnAir);
    document.getElementById('btn-reset-custom-time').addEventListener('click', () => {
      document.getElementById('custom-time-picker').value = '';
      renderNowOnAir();
    });

    document.getElementById('btn-reset-filters').addEventListener('click', () => {
      document.getElementById('global-search-input').value = '';
      document.getElementById('filter-language').value = 'farsi';
      document.getElementById('filter-category').value = 'all';
      document.getElementById('filter-band').value = 'all';
      document.getElementById('filter-confidence').value = 'all';
      document.getElementById('filter-sort').value = 'time-asc';
      renderAll();
    });

    // Theme Toggle
    const themeBtn = document.getElementById('btn-toggle-theme');
    let currentTheme = localStorage.getItem('iran_sw_theme') || 'dark';
    document.documentElement.setAttribute('data-theme', currentTheme);

    themeBtn.addEventListener('click', () => {
      currentTheme = currentTheme === 'dark' ? 'light' : 'dark';
      document.documentElement.setAttribute('data-theme', currentTheme);
      localStorage.setItem('iran_sw_theme', currentTheme);
    });

    // Emergency Mode Toggle
    const emBtn = document.getElementById('btn-toggle-emergency');
    emBtn.addEventListener('click', () => {
      IS_EMERGENCY = !IS_EMERGENCY;
      if (IS_EMERGENCY) {
        document.body.classList.add('emergency-mode');
        emBtn.textContent = 'خروج از حالت اضطراری';
        switchTab('tab-now');
      } else {
        document.body.classList.remove('emergency-mode');
        emBtn.textContent = '🚨 حالت اضطراری';
      }
      renderAll();
    });

    // Close modal on background click
    document.getElementById('station-modal').addEventListener('click', function(e) {
      if (e.target === this) closeModal();
    });

    // Initial Launch
    initHourSelector();
    renderAll();
  </script>
</body>
</html>
"""

def generate_html_app():
    json_path = os.path.join(DATA_DIR, 'radio-database.json')
    with open(json_path, 'r', encoding='utf-8') as f:
        db = json.load(f)
        
    db_json_str = json.dumps(db, ensure_ascii=False)
    final_html = HTML_TEMPLATE.replace('__EMBEDDED_DB_JSON__', db_json_str)
    
    out_file = os.path.join(APP_DIR, 'Iran-SW-Radio-Guide.html')
    with open(out_file, 'w', encoding='utf-8') as f:
        f.write(final_html)
    print(f"Generated Standalone Offline HTML: {out_file} ({len(final_html)} bytes)")

if __name__ == "__main__":
    generate_html_app()
