# 🎨 Badge Customization Guide

## Quick Reference for Badge Management

This guide helps you customize, update, and maintain the professional badges in your project.

---

## 📝 Current Badge Status

### Repository Badges (Update These)

The badges in README.md are **static** and need manual updates when values change:

| Badge | Current Value | Update When |
|-------|---------------|-------------|
| Version | 1.0.0 | New release published |
| Status | STABLE | Project status changes |
| Build | PASSING | Build status changes |
| Performance | 6.48M samples/sec | Performance benchmarks updated |
| Security Score | 92/100 | Security audit completed |
| Test Coverage | 95% | Test suite changes |
| Tests | 20 PASSED | Test count changes |

---

## 🔧 How to Update Badges

### Method 1: Direct URL Editing

Badges are created using shields.io URL format:
```
https://img.shields.io/badge/{LABEL}-{MESSAGE}-{COLOR}.svg?style={STYLE}
```

**Example:**
```markdown
![Version](https://img.shields.io/badge/version-1.0.0-blue.svg?style=for-the-badge)
```

**To update version to 2.0.0:**
```markdown
![Version](https://img.shields.io/badge/version-2.0.0-blue.svg?style=for-the-badge)
```

### Method 2: Using Python Script

Create `update_badges.py`:

```python
#!/usr/bin/env python3
"""Badge Update Helper Script"""

BADGE_TEMPLATES = {
    "version": "https://img.shields.io/badge/version-{value}-blue.svg?style=for-the-badge",
    "tests": "https://img.shields.io/badge/tests-{value}%20PASSED-success.svg?style=for-the-badge",
    "coverage": "https://img.shields.io/badge/coverage-{value}%25-brightgreen.svg?style=for-the-badge&logo=codecov",
    "security": "https://img.shields.io/badge/security%20score-{value}%2F100-brightgreen.svg?style=for-the-badge&logo=shield",
}

def generate_badge(badge_type: str, value: str) -> str:
    """Generate badge markdown"""
    url = BADGE_TEMPLATES[badge_type].format(value=value)
    label = badge_type.capitalize()
    return f"![{label}]({url})"

# Usage
print(generate_badge("version", "2.0.0"))
print(generate_badge("tests", "25"))
print(generate_badge("coverage", "97"))
print(generate_badge("security", "95"))
```

Run it:
```bash
python update_badges.py
```

### Method 3: Find and Replace

1. Open README.md
2. Find the badge you want to update
3. Replace the value in the URL

**Example - Update test count from 20 to 25:**
```bash
# Before
![Tests](https://img.shields.io/badge/tests-20%20PASSED-success.svg?style=for-the-badge)

# After
![Tests](https://img.shields.io/badge/tests-25%20PASSED-success.svg?style=for-the-badge)
```

---

## 🎨 Badge Customization Options

### Color Schemes

Choose colors that match your status:

| Color | Hex | Use For |
|-------|-----|---------|
| brightgreen | #44cc11 | Success, passing, excellent |
| green | #97ca00 | Good, working, secure |
| yellowgreen | #a4a61d | Acceptable, warning |
| yellow | #dfb317 | Caution, needs attention |
| orange | #fe7d37 | Important, moderate |
| red | #e05d44 | Critical, failed, security |
| blue | #007ec6 | Information, stable |
| lightgrey | #9f9f9f | Inactive, deprecated |

**Example - Change security badge to red for critical:**
```markdown
![Security](https://img.shields.io/badge/security-CRITICAL-red.svg?style=for-the-badge)
```

### Badge Styles

Available styles on shields.io:

| Style | Appearance | Use Case |
|-------|-----------|----------|
| `for-the-badge` | Large, bold | README header (current) |
| `flat` | Minimal | Feature lists |
| `flat-square` | Square corners | Modern look |
| `plastic` | Glossy | Eye-catching |
| `social` | GitHub-like | Social stats |

**Example - Switch to flat style:**
```markdown
![Version](https://img.shields.io/badge/version-1.0.0-blue.svg?style=flat)
```

### Adding Logos

Shields.io supports 100+ logos via Simple Icons:

```markdown
![Docker](https://img.shields.io/badge/docker-READY-2496ED.svg?style=for-the-badge&logo=docker&logoColor=white)
```

**Available logos:**
- `python`, `javascript`, `typescript`, `go`, `rust`
- `docker`, `kubernetes`, `aws`, `azure`, `gcp`
- `github`, `gitlab`, `bitbucket`
- `fastapi`, `django`, `flask`, `react`, `vue`

Find more at: https://simpleicons.org/

---

## 📊 Adding Dynamic Badges

### GitHub Repository Stats (Auto-updating)

Replace `username/repo` with your actual repository:

```markdown
<!-- Star count (updates automatically) -->
![GitHub Stars](https://img.shields.io/github/stars/username/repo?style=for-the-badge)

<!-- Fork count -->
![GitHub Forks](https://img.shields.io/github/forks/username/repo?style=for-the-badge)

<!-- Last commit -->
![Last Commit](https://img.shields.io/github/last-commit/username/repo?style=for-the-badge)

<!-- Contributors -->
![Contributors](https://img.shields.io/github/contributors/username/repo?style=for-the-badge)

<!-- Open issues -->
![Issues](https://img.shields.io/github/issues/username/repo?style=for-the-badge)

<!-- License -->
![License](https://img.shields.io/github/license/username/repo?style=for-the-badge)
```

### CI/CD Integration (Auto-updating)

**GitHub Actions:**
```markdown
![Build](https://github.com/username/repo/workflows/Tests/badge.svg)
```

**CircleCI:**
```markdown
![CircleCI](https://circleci.com/gh/username/repo.svg?style=shield)
```

**Travis CI:**
```markdown
![Travis](https://travis-ci.org/username/repo.svg?branch=main)
```

### Code Coverage (Auto-updating)

**Codecov:**
```markdown
![Codecov](https://codecov.io/gh/username/repo/branch/main/graph/badge.svg)
```

**Coveralls:**
```markdown
![Coverage](https://coveralls.io/repos/github/username/repo/badge.svg?branch=main)
```

### Package Registries (Auto-updating)

**PyPI:**
```markdown
![PyPI](https://img.shields.io/pypi/v/package-name?style=for-the-badge)
![Downloads](https://img.shields.io/pypi/dm/package-name?style=for-the-badge)
```

**npm:**
```markdown
![npm](https://img.shields.io/npm/v/package-name?style=for-the-badge)
![Downloads](https://img.shields.io/npm/dm/package-name?style=for-the-badge)
```

---

## 🔄 Maintenance Schedule

### Regular Updates (After Each Change)

| Badge | Update Frequency | Trigger |
|-------|-----------------|---------|
| Version | After release | `git tag v1.0.1` |
| Build Status | After CI run | Automated if using GitHub Actions |
| Test Count | After adding tests | Count test files |
| Coverage | After test changes | Run coverage report |

### Periodic Updates (Monthly/Quarterly)

| Badge | Update Frequency | How to Check |
|-------|-----------------|--------------|
| Security Score | Quarterly | Run security audit |
| Performance | After optimization | Run benchmarks |
| Code Quality | Monthly | Run linter/analyzer |

### Automation Script

Create `.github/scripts/update_badges.sh`:

```bash
#!/bin/bash
# Automated badge update script

# Get current version from git tags
VERSION=$(git describe --tags --abbrev=0 | sed 's/v//')

# Count test files
TESTS=$(find tests -name "test_*.py" | wc -l | xargs)

# Get coverage from pytest
COVERAGE=$(pytest --cov --cov-report=term | grep TOTAL | awk '{print $4}' | sed 's/%//')

# Update README.md
sed -i "s/version-[0-9.]*-blue/version-${VERSION}-blue/g" README.md
sed -i "s/tests-[0-9]*%20PASSED/tests-${TESTS}%20PASSED/g" README.md
sed -i "s/coverage-[0-9]*%25/coverage-${COVERAGE}%25/g" README.md

echo "✅ Badges updated:"
echo "   Version: ${VERSION}"
echo "   Tests: ${TESTS}"
echo "   Coverage: ${COVERAGE}%"
```

Run it:
```bash
chmod +x .github/scripts/update_badges.sh
./.github/scripts/update_badges.sh
```

---

## 🎯 Badge Best Practices

### Do's ✅

- **Keep badges accurate** - Update immediately when values change
- **Use consistent style** - Stick to one style (we use `for-the-badge`)
- **Group logically** - Status, Performance, Quality, Technology
- **Use appropriate colors** - Green for success, red for critical
- **Add logos** - Makes badges more recognizable
- **Limit count** - 15-20 badges maximum for readability

### Don'ts ❌

- **Don't overload** - Too many badges overwhelm readers
- **Don't fake metrics** - Only show real, verifiable data
- **Don't use conflicting colors** - Stick to standard color meanings
- **Don't mix styles** - Inconsistent styling looks unprofessional
- **Don't forget to update** - Outdated badges hurt credibility
- **Don't link broken URLs** - Test all badge links

---

## 🛠️ Troubleshooting

### Badge Not Displaying

**Problem:** Badge shows as broken image
**Solution:**
1. Check URL encoding (spaces should be `%20`)
2. Verify shields.io is accessible
3. Test URL in browser directly

### Badge Shows Wrong Value

**Problem:** Badge displays outdated information
**Solution:**
1. Clear browser cache
2. Force refresh shields.io: add `?cache=none` to URL
3. Update the URL in README.md

### Badge URL Too Long

**Problem:** Complex badges create messy markdown
**Solution:**
Use reference-style links:
```markdown
[version-badge]: https://img.shields.io/badge/version-1.0.0-blue.svg?style=for-the-badge
[status-badge]: https://img.shields.io/badge/status-STABLE-success.svg?style=for-the-badge

![Version][version-badge]
![Status][status-badge]
```

---

## 📚 Additional Resources

### Official Documentation
- **Shields.io**: https://shields.io/
- **Simple Icons**: https://simpleicons.org/
- **Badge Guide**: https://github.com/badges/shields

### Badge Generators
- **Shields.io Editor**: https://shields.io/
- **Badge Maker**: https://badgemaker.org/
- **For The Badge**: https://forthebadge.com/

### Color Tools
- **Color Picker**: https://htmlcolorcodes.com/
- **Palette Generator**: https://coolors.co/

---

## 📝 Quick Update Checklist

When releasing a new version, update these badges:

- [ ] Version badge - Update to new version number
- [ ] Status badge - Confirm still "STABLE" or change if needed
- [ ] Build badge - Ensure shows "PASSING"
- [ ] Test count - Update if tests added/removed
- [ ] Coverage - Update with latest coverage percentage
- [ ] Performance - Update if benchmarks improved
- [ ] Security score - Update if security audit run
- [ ] Technology versions - Update dependency versions if upgraded

---

## 💡 Advanced Customization

### Custom Badge Server

For sensitive data, host your own badge server:

```python
from flask import Flask, send_file
from pybadges import badge

app = Flask(__name__)

@app.route('/badge/<label>/<message>/<color>')
def custom_badge(label, message, color):
    s = badge(left_text=label, right_text=message, right_color=color)
    return s, 200, {'Content-Type': 'image/svg+xml'}

if __name__ == '__main__':
    app.run(port=5000)
```

Use in README:
```markdown
![Custom](http://your-server.com/badge/label/message/color)
```

### Dynamic Badges with GitHub Actions

Create `.github/workflows/update-badges.yml`:

```yaml
name: Update Badges

on:
  push:
    branches: [main]

jobs:
  update-badges:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Update version badge
        run: |
          VERSION=$(cat VERSION)
          sed -i "s/version-[0-9.]*-blue/version-${VERSION}-blue/g" README.md

      - name: Commit changes
        run: |
          git config --local user.email "action@github.com"
          git config --local user.name "GitHub Action"
          git add README.md
          git commit -m "Update badges [skip ci]" || exit 0
          git push
```

---

**For more examples, see `BADGES.md` for the complete badge collection!** 🎨
