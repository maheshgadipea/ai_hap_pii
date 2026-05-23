# ai_hap_pii

Detect and mask PII (Personally Identifiable Information) and detect HAP (Hate, Abuse, Profanity) in any text query, packaged as a Docker CLI tool.

- **PII** — powered by [`commonregex-improved`](https://pypi.org/project/commonregex-improved/)
- **HAP** — powered by [`detoxify`](https://github.com/unitaryai/detoxify) using `toxic-bert`

---

## Detected PII Types

| Type | Example |
|---|---|
| Emails | `john@example.com` |
| Phone numbers | `(555) 123-4567` |
| SSNs | `269-43-3219` |
| IPv4 / IPv6 addresses | `192.168.1.100` |
| Credit card numbers | `4111-1111-1111-1111` |
| Bitcoin addresses | `1A1zP1eP5QGefi2DMPTfTL5SLmv7Divf` |
| Links / URLs | `example.com` |
| Dates & times | `Jan 9th 2012`, `5:00PM` |
| Prices | `$1000` |
| Street addresses | `123 Main Street` |
| ZIP codes, PO boxes | `90210` |
| MAC addresses | `00:1A:2B:3C:4D:5E` |
| IBAN numbers | `GB82WEST12345698765432` |
| MD5 / SHA1 / SHA256 hashes | `d41d8cd98f00b204e9800998ecf8427e` |
| ISBN-10 / ISBN-13 | `978-0-13-468599-1` |
| Git repos | `https://github.com/org/repo.git` |
| Hex colors | `#FF5733` |

## HAP Categories

| Category | Description |
|---|---|
| `toxicity` | General toxic content |
| `severe_toxicity` | Severely toxic content |
| `obscene` | Obscene or vulgar language |
| `threat` | Threatening language |
| `insult` | Insults directed at others |
| `identity_attack` | Attacks based on identity |

---

## Setup

**Requirements:** Docker, [HuggingFace CLI](https://huggingface.co/docs/huggingface_hub/guides/cli)

### 1. Clone the repo

```bash
git clone https://github.com/yourusername/ai_hap_pii.git
cd ai_hap_pii
```

### 2. Download the toxic-bert ONNX model

```bash
hf download Xenova/toxic-bert --local-dir ./models/models/toxic-bert-onnx
```

### 3. Build the Docker image

```bash
docker build -t pii-hap-detector .
```

---

## Usage

The CLI has three subcommands: `pii`, `hap`, and `both`.

### PII — detect and mask PII

```bash
docker run --rm pii-hap-detector pii --mask placeholder "Call me at (555) 123-4567 or john@example.com"
```
```
=== PII Masked Output ===
Call me at <PHONES> or <EMAILS>

=== Detected PII ===
  phones: ['(555) 123-4567']
  emails: ['john@example.com']
```

### HAP — detect hate, abuse, profanity

```bash
docker run --rm pii-hap-detector hap "I hate you, you are disgusting."
```
```
=== HAP Analysis ===
  toxicity                  0.9936  [FLAGGED]
  severe_toxicity           0.0431
  obscene                   0.6895  [FLAGGED]
  threat                    0.0022
  insult                    0.9485  [FLAGGED]
  identity_attack           0.0198

Overall: FLAGGED (threshold: 0.5)
```

### Both — run PII masking and HAP analysis together

```bash
docker run --rm pii-hap-detector both --mask placeholder "Email john@example.com — I hate you!"
```

### Stdin

```bash
echo "My SSN is 269-43-3219" | docker run --rm -i pii-hap-detector pii --mask redacted
```

---

## PII Masking Modes

| Flag | Example output |
|---|---|
| `--mask partial` | `j**************m` (default) |
| `--mask stars` | `****************` |
| `--mask placeholder` | `<EMAILS>` |
| `--mask redacted` | `[REDACTED-EMAILS]` |

## HAP Threshold

Use `--threshold` to adjust sensitivity (default: `0.5`):

```bash
docker run --rm pii-hap-detector hap --threshold 0.3 "some borderline text"
```

---

## Test Examples

### PII tests

```bash
# 1. Personal contact info — email, phone, zip code
docker run --rm pii-hap-detector pii --mask placeholder "Hi, I'm Alice Johnson. You can reach me at alice.johnson@gmail.com or call me at +1 (408) 555-0192. I live at 742 Evergreen Terrace, Springfield, IL 62704."

# 2. Payment record — credit card, IBAN, price
docker run --rm pii-hap-detector pii --mask placeholder "Payment processed for card 4532-0151-1283-0366. Transaction ID linked to account IBAN: GB29NWBK60161331926819. Amount charged: \$1,299.99."

# 3. Security incident log — IPv4, IPv6, port
docker run --rm pii-hap-detector pii --mask placeholder "Server breach detected at IP 203.0.113.45. Suspicious traffic also from IPv6 2001:0db8:85a3:0000:0000:8a2e:0370:7334 on port 8443."

# 4. Medical / ID record — SSN, dates, time
docker run --rm pii-hap-detector pii --mask placeholder "My SSN is 572-88-3416 and my passport was issued on March 15th 2019. Date of birth: 04/07/1985. Appointment at 3:30PM."

# 5. Dev / DevOps commit — git link, SHA256 hash
docker run --rm pii-hap-detector pii --mask placeholder "Repo cloned from https://github.com/acme-corp/secret-service.git. Commit hash (SHA256): a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3"

# 6. Crypto transaction — BTC address, MD5 hash
docker run --rm pii-hap-detector pii --mask placeholder "Send Bitcoin to 1BvBMSEYstWetqTFn5Au4m4GFg7xJaNVN2 for the invoice. The seller's Ethereum backup key MD5 is 098f6bcd4621d373cade4e832627b4f6."

# 7. Network scan report — MAC, IPv4, ports, hex color
docker run --rm pii-hap-detector pii --mask placeholder "Network scan found device MAC 00:14:22:01:23:45 at 10.0.0.254. Open ports include 3306 and 27017. Color code for alert UI: #E74C3C."

# 8. Library / order record — ISBN-13, ISBN-10, price, PO box, zip
docker run --rm pii-hap-detector pii --mask placeholder "Book reference ISBN-13: 978-0-13-468599-1 and ISBN-10: 0-13-468599-X. Published price \$59.00. Order PO Box 1234, Austin TX 78701."

# 9. Support ticket — email, phone+ext, Visa card, time, date
docker run --rm pii-hap-detector pii --mask placeholder "Support ticket from bob_smith@company.org, ph: 1-800-555-0199 x204. Visa ending 4916338506082832 was declined at 11:45AM on Feb 2nd 2024."

# 10. Infrastructure log — SHA1, git repo, IPv4, time
docker run --rm pii-hap-detector pii --mask placeholder "SHA1 of config backup: da39a3ee5e6b4b0d3255bfef95601890afd80709. Deployed via git@github.com:myorg/infra.git. Admin logged in from 172.16.254.1 at 9:00AM."
```

### HAP tests

```bash
# 1. Angry customer support message
docker run --rm pii-hap-detector hap "Your service is absolutely terrible. You people are incompetent idiots and I hope your company burns down."

# 2. Social media comment — identity attack
docker run --rm pii-hap-detector hap "People like you don't belong in this country. Go back to where you came from, you don't deserve to be here."

# 3. Online gaming toxicity
docker run --rm pii-hap-detector hap "You are the worst player I have ever seen. Uninstall the game you brain-dead loser, nobody wants you here."

# 4. Workplace harassment
docker run --rm pii-hap-detector hap "If you take my parking spot one more time I swear you will regret it. Watch your back."

# 5. Political comment — borderline
docker run --rm pii-hap-detector hap "Politicians are all corrupt liars. They don't care about us, they never have and never will."

# 6. Clean professional message — should show CLEAN
docker run --rm pii-hap-detector hap "Hi team, please review the attached report and share your feedback by Friday. Thank you."

# 7. Product review frustration — borderline
docker run --rm pii-hap-detector hap "This product is garbage. Complete waste of money. The company that made this should be ashamed of themselves."

# 8. Direct threat
docker run --rm pii-hap-detector hap "I know where you live and I will make sure you pay for what you did to me."

# 9. Religious hate speech
docker run --rm pii-hap-detector hap "People who follow that religion are all dangerous extremists and should not be trusted."

# 10. Lowering threshold to 0.2 — catch borderline frustration
docker run --rm pii-hap-detector hap --threshold 0.2 "Ugh, I can't stand how stupid this software is. It crashes every single time."
```

### Both PII + HAP tests

```bash
# 1. Abusive message with contact info
docker run --rm pii-hap-detector both --mask placeholder "Email me at hate@example.com you disgusting fool, I hate everything about you."

# 2. Threatening message with SSN
docker run --rm pii-hap-detector both --mask redacted "My SSN is 572-88-3416 — give me what I want or you'll regret it."

# 3. Clean message with PII — should show CLEAN for HAP
docker run --rm pii-hap-detector both --mask partial "Please contact alice@company.com or call (555) 987-6543 for your appointment on Jan 10th."
```

---

## Project Structure

```
ai_hap_pii/
├── detector.py       # Unified CLI entry point (pii / hap / both)
├── pii_detector.py   # PII detection and masking logic
├── hap_detector.py   # HAP analysis using toxic-bert
├── requirements.txt  # Python dependencies
├── Dockerfile        # Python 3.13.3-slim + pre-downloaded toxic-bert
└── README.md
```
