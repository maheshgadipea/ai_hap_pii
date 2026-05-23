# ai_hap_pii

Detect and mask PII (Personally Identifiable Information) in any text query, packaged as a Docker CLI tool.

Built with [`commonregex-improved`](https://pypi.org/project/commonregex-improved/).

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

## Setup

**Requirements:** Docker

```bash
# Clone and build
git clone https://github.com/yourusername/ai_hap_pii.git
cd ai_hap_pii
docker build -t pii-detector .
```

## Usage

### CLI argument

```bash
docker run --rm pii-detector "Call me at (555) 123-4567 or john@example.com"
```

### Stdin

```bash
echo "My SSN is 269-43-3219" | docker run --rm -i pii-detector
```

## Masking Modes

Control output with the `--mask` flag (default: `partial`).

### `partial` — show first and last character

```bash
docker run --rm pii-detector --mask partial "Call me at (555) 123-4567 or john@example.com"
```
```
=== Masked Output ===
Call me at (************7 or j**************m
```

### `stars` — replace every character with `*`

```bash
docker run --rm pii-detector --mask stars "Call me at (555) 123-4567 or john@example.com"
```
```
=== Masked Output ===
Call me at ***** ******** or ****************
```

### `placeholder` — replace with `<TYPE>` tag

```bash
docker run --rm pii-detector --mask placeholder "Call me at (555) 123-4567 or john@example.com"
```
```
=== Masked Output ===
Call me at <PHONE> or <EMAIL>
```

### `redacted` — replace with `[REDACTED-TYPE]` label

```bash
docker run --rm pii-detector --mask redacted "Call me at (555) 123-4567 or john@example.com"
```
```
=== Masked Output ===
Call me at [REDACTED-PHONE] or [REDACTED-EMAIL]
```

## Output Format

Each run prints the masked text and a breakdown of all detected PII:

```
=== Masked Output ===
Call me at <PHONE> or <EMAIL>

=== Detected PII ===
  emails: ['john@example.com']
  phones: ['(555) 123-4567']
```

## Test Examples

10 real-world scenarios covering all supported PII types. Swap `--mask placeholder` with `partial`, `stars`, or `redacted` on any command.

```bash
# 1. Personal contact info — email, phone, zip code
docker run --rm pii-detector --mask placeholder "Hi, I'm Alice Johnson. You can reach me at alice.johnson@gmail.com or call me at +1 (408) 555-0192. I live at 742 Evergreen Terrace, Springfield, IL 62704."

# 2. Payment record — credit card, IBAN, price
docker run --rm pii-detector --mask placeholder "Payment processed for card 4532-0151-1283-0366. Transaction ID linked to account IBAN: GB29NWBK60161331926819. Amount charged: \$1,299.99."

# 3. Security incident log — IPv4, IPv6, port
docker run --rm pii-detector --mask placeholder "Server breach detected at IP 203.0.113.45. Suspicious traffic also from IPv6 2001:0db8:85a3:0000:0000:8a2e:0370:7334 on port 8443."

# 4. Medical / ID record — SSN, dates, time
docker run --rm pii-detector --mask placeholder "My SSN is 572-88-3416 and my passport was issued on March 15th 2019. Date of birth: 04/07/1985. Appointment at 3:30PM."

# 5. Dev / DevOps commit — git link, SHA256 hash
docker run --rm pii-detector --mask placeholder "Repo cloned from https://github.com/acme-corp/secret-service.git. Commit hash (SHA256): a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3"

# 6. Crypto transaction — BTC address, MD5 hash
docker run --rm pii-detector --mask placeholder "Send Bitcoin to 1BvBMSEYstWetqTFn5Au4m4GFg7xJaNVN2 for the invoice. The seller's Ethereum backup key MD5 is 098f6bcd4621d373cade4e832627b4f6."

# 7. Network scan report — MAC, IPv4, ports, hex color
docker run --rm pii-detector --mask placeholder "Network scan found device MAC 00:14:22:01:23:45 at 10.0.0.254. Open ports include 3306 and 27017. Color code for alert UI: #E74C3C."

# 8. Library / order record — ISBN-13, ISBN-10, price, PO box, zip
docker run --rm pii-detector --mask placeholder "Book reference ISBN-13: 978-0-13-468599-1 and ISBN-10: 0-13-468599-X. Published price \$59.00. Order PO Box 1234, Austin TX 78701."

# 9. Support ticket — email, phone+ext, Visa card, time, date
docker run --rm pii-detector --mask placeholder "Support ticket from bob_smith@company.org, ph: 1-800-555-0199 x204. Visa ending 4916338506082832 was declined at 11:45AM on Feb 2nd 2024."

# 10. Infrastructure log — SHA1, git repo, IPv4, time
docker run --rm pii-detector --mask placeholder "SHA1 of config backup: da39a3ee5e6b4b0d3255bfef95601890afd80709. Deployed via git@github.com:myorg/infra.git. Admin logged in from 172.16.254.1 at 9:00AM."
```

## Project Structure

```
ai_hap_pii/
├── pii_detector.py   # Detection and masking logic
├── requirements.txt  # Python dependencies
├── Dockerfile        # Python 3.13.3-slim image
└── README.md
```
