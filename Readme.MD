![Compressor Bot](https://telegra.ph/file/7e3c7f4f70272c6e59c52.jpg)

# Erika Amano — Telegram Video Encoder Bot

> Erika Amano (天野 エリカ, Amano Erika) — named after the main female protagonist of *A Couple of Cuckoos*.

A powerful, feature-rich Telegram bot for video encoding. Leverages Telegram's unlimited cloud storage to help users reduce video file sizes while maintaining quality — perfect for users on limited mobile data.

Built with **Telethon** + **async MongoDB (Motor)** + **FFmpeg**.

---

## ✨ Features

### Core Encoding
| Feature | Description |
|---------|-------------|
| Multi-user support | Authorization system with request/approve workflow |
| Queue system | Position tracking, parallel encoding support |
| Inline settings | Resolution, CRF, Preset, Codec, Audio — all via buttons |
| Smart captions | Auto thumbnail extraction + before/after file size comparison |
| Audio detection | Automatically skips audio mapping if no audio stream found |
| 4GB uploads | Optional userbot via `SESSION_STRING` for large file uploads |

### Advanced Encoding
| Feature | Command | Description |
|---------|---------|-------------|
| HW acceleration | `/hwaccel` | NVENC, VAAPI, or auto-detect |
| Custom rename | `/rename` | Pattern: `[Tag] {title} [{res}].{ext}` |
| Trim/cut | `/trim` | Reply to video: `/trim 00:05:00 00:45:00` |
| Track selection | `/tracks` | Select audio/subtitle tracks: `/tracks audio 0,1` |
| Watermark | `/watermark` | Text overlay or image watermark |
| Profiles | `/profile` | Save/load/delete encoding presets |
| Sample clip | `/sample` | Generate preview: `/sample 30` |

### Queue & Scheduling
| Feature | Description |
|---------|-------------|
| Parallel encoding | Configurable `MAX_CONCURRENT` workers |
| Scheduled encoding | `/schedule off-peak\|night\|HH:MM-HH:MM` |
| Queue persistence | Survives bot restarts (MongoDB-backed) |
| Auto-delete | `/autodelete` — Remove originals after encoding |

### User Management
| Feature | Command | Description |
|---------|---------|-------------|
| Ban system | `/ban`, `/unban`, `/bans` | Block abusive users |
| Daily quota | `DAILY_QUOTA` env var | Limit encodes per user per day |
| File size limit | `MAX_FILE_SIZE` env var | Reject files exceeding limit |
| Auto-authorize | `AUTO_AUTH` env var | Skip manual approval |
| Maintenance mode | `/maintenance on/off` | Pause all encoding with custom message |

### Monitoring & History
| Feature | Command | Description |
|---------|---------|-------------|
| Encoding history | `/history` | Last 10 encodes with size/duration stats |
| Notifications | `NOTIFICATION_CHANNEL` | Post completed encodes to a channel |
| Statistics | `/stats` | Users, bans, queue, space saved, history count |
| Logs | `/log` | Download bot log file |
| Broadcast | `/broadcast` | Message all users at once |

---

## 📋 Command Reference

### User Commands
| Command | Description |
|---------|-------------|
| `/start` | Start bot & show help |
| `/help` | Feature overview with inline buttons |
| `/settings` | View all settings at a glance |
| `/cancel` | Cancel current encoding |
| `/queue` | View queue status & position |
| `/rename <pattern>` | Set output filename pattern (`{title}`, `{res}`, `{codec}`, `{ext}`) |
| `/trim <start> <end>` | Trim video before encoding (reply to video) |
| `/sample [seconds]` | Generate preview clip (reply to video, default 30s) |
| `/tracks` | View/set audio & subtitle tracks (reply to video to analyze) |
| `/profile save\|load\|delete\|list <name>` | Manage encoding presets |
| `/watermark <text\|off>` | Set text watermark (reply to image for image watermark) |
| `/schedule <off-peak\|night\|HH:MM-HH:MM\|off>` | Set encoding time window |
| `/autodelete` | Toggle auto-delete of original messages |
| `/hwaccel <auto\|nvenc\|vaapi\|none>` | Set hardware acceleration |
| `/history` | View recent encoding history |

### Admin Commands (Owner Only)
| Command | Description |
|---------|-------------|
| `/users` | List all authorized users |
| `/broadcast <msg>` | Send message to all users |
| `/ban <user_id> [reason]` | Ban a user |
| `/unban <user_id>` | Unban a user |
| `/bans` | List all banned users |
| `/maintenance on\|off [msg]` | Toggle maintenance mode |
| `/stats` | Comprehensive bot statistics |
| `/log` | Get bot error log |
| `/eval <code>` | Execute Python code |
| `/term <cmd>` | Execute shell command |
| `/info` | Get user information |

---

## ⚙️ Variables

### Required
| Variable | Description |
|----------|-------------|
| `BOT_TOKEN` | Get from [@BotFather](https://t.me/BotFather) |
| `API_ID` | Get from [my.telegram.org](https://my.telegram.org) |
| `API_HASH` | Get from [my.telegram.org](https://my.telegram.org) |
| `OWNER_ID` | Your Telegram user ID (numeric) |
| `MONGO_DB` | MongoDB connection URI ([cloud.mongodb.com](https://cloud.mongodb.com)) |

### Optional
| Variable | Default | Description |
|----------|---------|-------------|
| `FILES_CHANNEL` | — | Channel ID for file storage (e.g. `-10037823545`) |
| `BOT_NAME` | `Erika` | Bot name for DB collection |
| `SESSION_STRING` | — | Telethon StringSession for 4GB uploads |
| `TRIGGERS` | `/ !` | Command prefixes |

### Feature Toggles
| Variable | Default | Description |
|----------|---------|-------------|
| `AUTO_AUTH` | `false` | Auto-authorize new users |
| `MAX_CONCURRENT` | `1` | Max parallel encoding tasks |
| `MAX_FILE_SIZE` | `0` | Max input file size in bytes (`0` = unlimited) |
| `DAILY_QUOTA` | `0` | Max encodes per user per day (`0` = unlimited) |
| `NOTIFICATION_CHANNEL` | — | Channel ID to post completed encodes |
| `WATERMARK_TEXT` | — | Default text watermark overlay |
| `WATERMARK_IMAGE` | — | Path to default watermark image |
| `HW_ACCEL` | `auto` | Hardware acceleration (`auto`/`nvenc`/`vaapi`/`none`) |

> **Note:** The bot won't start without setting all **Required** variables.

---

## 🚀 Deploy

### Docker Deploy
```bash
git clone https://github.com/The-Hunter-Oraganization/Erika-Amano.git
cd Erika-Amano
cp .env.example .env
# Edit .env with your variables
docker-compose up -d
```

### Local Deploy
```bash
sudo apt install python3 python3-pip ffmpeg -y
git clone https://github.com/The-Hunter-Oraganization/Erika-Amano.git
cd Erika-Amano
pip3 install -r requirements.txt
cp .env.example .env
# Edit .env with your variables
python3 -m Bot
```

### Heroku Deploy

<p align="center"><a href="https://heroku.com/deploy?template=https://github.com/The-Hunter-Oraganization/Erika-Amano"> <img src="https://img.shields.io/badge/Deploy%20To%20Heroku-black?style=for-the-badge&logo=heroku" width="220" height="38.45"/></a></p>

---

## 📁 Project Structure
```
Erika-Amano/
├── Bot/
│   ├── __init__.py          # Config & client initialization
│   ├── __main__.py          # Entry point & plugin loader
│   ├── plugins/
│   │   ├── admin.py         # Owner commands (ban, maintenance, stats)
│   │   ├── callback.py      # Inline buttons & settings UI
│   │   ├── encoder.py       # Core encoding pipeline & queue
│   │   ├── features.py      # User feature commands
│   │   ├── eval.py          # Code execution (owner only)
│   │   ├── extra.py         # Miscellaneous handlers
│   │   ├── user_info.py     # User info command
│   │   └── database/
│   │       └── mongo_db.py  # Async MongoDB wrapper
│   └── utils/
│       ├── decorators.py    # FFmpeg command builder
│       ├── ffmpeg.py        # FFmpeg execution & progress
│       ├── progress_pyro.py # Upload/download progress
│       └── user_info.py     # User info helpers
├── .env.example
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── Readme.MD
```

---

## Credits
- **Developer:** [Sohail](https://t.me/sohailkhan_indianime)
- **GitHub:** [soheru](https://github.com/soheru)
- **Channel:** [aboutmesk](https://t.me/aboutmesk)
