# Webhook Architecture Guide

## Overview

This document explains the centralized webhook hub architecture, when to use it, and alternatives.

## Current Architecture: Centralized Webhook Hub

```
                    GitHub Organization
                            │
                  ┌─────────┴─────────┐
                  │                   │
           Repo A Issues       Repo B Issues
                  │                   │
                  └─────────┬─────────┘
                            │
                    Organization Webhook
                    (Single URL)
                            │
                            ↓
         ┌──────────────────────────────────────┐
         │  agentic-coding-library              │
         │  (Centralized Webhook Server)        │
         │                                      │
         │  ┌────────────────────────────────┐ │
         │  │  Webhook Receiver              │ │
         │  │  - Receives all org events     │ │
         │  │  - Clones repos to repos/      │ │
         │  │  - Installs plugin             │ │
         │  │  - Executes workflows          │ │
         │  └────────────────────────────────┘ │
         │                                      │
         │  repos/                              │
         │  ├── repo-a/ (cloned)               │
         │  │   ├── tac-core-plugin/           │
         │  │   └── trees/ (worktrees)         │
         │  ├── repo-b/ (cloned)               │
         │  │   ├── tac-core-plugin/           │
         │  │   └── trees/ (worktrees)         │
         │  └── ...                             │
         │                                      │
         │  tac-core-plugin/ (source)          │
         │  adw/ (workflows)                   │
         └──────────────────────────────────────┘
```

## When to Use Centralized Webhook Hub

### ✅ Good For:

**1. Small to Medium Organizations (5-30 repos)**
- Easy to manage single server
- Cost-effective (one server, one domain)
- Simple setup and maintenance

**2. Similar Repositories**
- All repos use similar tech stack
- Shared coding patterns
- Common workflow needs

**3. Limited Resources**
- Small team (1-10 developers)
- Limited budget
- Don't want to manage infrastructure per-repo

**4. Experimental/Learning Phase**
- Testing AI developer workflows
- Iterating on ADW system
- Want centralized control to update quickly

**5. Moderate Workflow Frequency**
- Few webhooks per hour
- Not mission-critical latency requirements
- Can tolerate occasional delays

### ❌ Not Good For:

**1. Large Organizations (100+ repos)**
- Single server becomes bottleneck
- Disk space grows too large
- Maintenance becomes complex

**2. High-Frequency Workflows**
- Dozens of webhooks per hour
- Need <5 second response times
- Mission-critical automation

**3. Diverse Repository Types**
- Different languages, frameworks
- Different security requirements
- Different teams with different needs

**4. Strict Security Requirements**
- Can't have all repo code on one server
- Need isolated environments per team
- Compliance requirements (SOC2, HIPAA, etc.)

**5. Geographic Distribution**
- Teams in different regions
- Latency-sensitive operations
- Data sovereignty requirements

## Alternative Architectures

### Alternative 1: Per-Repo Webhooks (Distributed)

```
Repo A                     Repo B                     Repo C
  │                          │                          │
  │ Webhook                  │ Webhook                  │ Webhook
  ↓                          ↓                          ↓
Server A                   Server B                   Server C
- Dedicated server         - Dedicated server         - Dedicated server
- Only serves Repo A       - Only serves Repo B       - Only serves Repo C
- No shared resources      - No shared resources      - No shared resources
```

**Pros:**
- ✅ No bottleneck (each repo has own resources)
- ✅ Isolated failures (one repo's issues don't affect others)
- ✅ Scales horizontally
- ✅ Can customize per repo

**Cons:**
- ❌ More complex to manage (N servers for N repos)
- ❌ Higher cost (N servers + N domains)
- ❌ Harder to update ADW system across all repos
- ❌ Each repo needs its own webhook setup

**When to use:**
- Large organizations (50+ repos)
- High security requirements
- Different teams/departments
- Budget for infrastructure

### Alternative 2: Hybrid (Queue-Based Hub)

```
                    GitHub Organization
                            │
                  ┌─────────┴─────────┐
                  │                   │
           Repo A Issues       Repo B Issues
                  │                   │
                  └─────────┬─────────┘
                            │
                    Organization Webhook
                            │
                            ↓
         ┌──────────────────────────────────────┐
         │  Webhook Receiver (Fast)             │
         │  - Accepts webhook                   │
         │  - Adds to queue                     │
         │  - Returns 200 immediately           │
         └──────────────────────────────────────┘
                            │
                            ↓
         ┌──────────────────────────────────────┐
         │  Redis/RabbitMQ Queue                │
         └──────────────────────────────────────┘
                            │
              ┌─────────────┼─────────────┐
              ↓             ↓             ↓
         Worker 1       Worker 2      Worker 3
         (Process)      (Process)     (Process)
```

**Pros:**
- ✅ Fast webhook response (no timeout risk)
- ✅ Control concurrency (limit to N workers)
- ✅ Retry failed workflows automatically
- ✅ Monitor queue depth and performance
- ✅ Can scale workers independently

**Cons:**
- ❌ More complex setup (need Redis/RabbitMQ)
- ❌ Another service to maintain
- ❌ Still centralized (single queue)

**When to use:**
- Medium to high webhook frequency
- Need reliable retry mechanism
- Want to control resource usage
- Ready for some complexity

### Alternative 3: GitHub Actions (No Server)

```
Repo A
  │
  │ GitHub Issue Created
  ↓
  GitHub Actions Workflow
  - Runs in GitHub's infrastructure
  - No server needed
  - Executes ADW workflow
  - Creates PR
```

**Pros:**
- ✅ No server to maintain
- ✅ No infrastructure costs
- ✅ Built-in secrets management
- ✅ GitHub UI for monitoring

**Cons:**
- ❌ Limited to 6 hours per workflow
- ❌ Slower (cold start each time)
- ❌ Harder to debug
- ❌ Less control over environment
- ❌ Costs GitHub Actions minutes

**When to use:**
- Don't want to manage servers
- Low to medium frequency
- Simple workflows (<1 hour)
- Already using GitHub Actions

## Architecture Comparison

| Factor | Centralized Hub | Per-Repo | Queue-Based | GitHub Actions |
|--------|----------------|----------|-------------|----------------|
| **Setup Complexity** | 🟢 Low | 🔴 High | 🟡 Medium | 🟢 Low |
| **Maintenance** | 🟢 Single server | 🔴 N servers | 🟡 Queue + workers | 🟢 None |
| **Cost** | 🟢 Low | 🔴 High | 🟡 Medium | 🟡 Actions minutes |
| **Scalability** | 🔴 Limited | 🟢 Excellent | 🟡 Good | 🟡 Good |
| **Performance** | 🟡 Good | 🟢 Excellent | 🟢 Excellent | 🔴 Slow (cold start) |
| **Flexibility** | 🟢 Easy to update | 🔴 Update N times | 🟢 Easy to update | 🟡 YAML config |
| **Debugging** | 🟢 Easy | 🟡 Medium | 🟡 Medium | 🔴 Hard |
| **Security** | 🔴 All repos on one server | 🟢 Isolated | 🔴 All repos on one server | 🟢 Isolated |

## Migration Paths

### From Centralized → Queue-Based

**When disk usage >50GB or webhooks >20/hour:**

1. Install Redis:
   ```bash
   brew install redis
   redis-server
   ```

2. Update webhook to add jobs to queue instead of executing directly

3. Create worker processes that pull from queue

4. Scale workers based on queue depth

**Effort:** Medium (1-2 days)

### From Centralized → Per-Repo

**When repos >50 or teams want isolation:**

1. For each repo, set up dedicated webhook server
2. Copy tac-core-plugin (contains adw_modules) to each
3. Configure per-repo webhook in GitHub
4. Decommission centralized server

**Effort:** High (1 week+)

### From Centralized → GitHub Actions

**When want zero maintenance:**

1. Create `.github/workflows/adw-automation.yml` in each repo
2. Convert ADW workflows to GitHub Actions syntax
3. Test with sample issues
4. Decommission webhook server

**Effort:** Medium (2-3 days per repo)

## Decision Tree

```
Start here
    │
    ├─ Do you have >50 repos?
    │  ├─ Yes → Use Per-Repo Webhooks
    │  └─ No → Continue
    │
    ├─ Do you have >20 webhooks/hour?
    │  ├─ Yes → Use Queue-Based Hub
    │  └─ No → Continue
    │
    ├─ Do you want zero server maintenance?
    │  ├─ Yes → Use GitHub Actions
    │  └─ No → Continue
    │
    ├─ Do you have strict security requirements?
    │  ├─ Yes → Use Per-Repo Webhooks
    │  └─ No → Continue
    │
    └─ Use Centralized Hub (Current)
       ✅ Best for: 5-30 repos, <20 webhooks/hour, small teams
```

## Monitoring Thresholds

### Yellow Flags (Plan Migration)
- Disk usage >50GB
- Webhooks >10/hour sustained
- CPU usage >60% average
- Cleanup runs weekly
- Repo count >30

### Red Flags (Migrate Now)
- Disk usage >80%
- Webhooks >20/hour sustained
- CPU usage >80% average
- Webhook delays >30 seconds
- Repo count >50
- Out of disk space incidents

## Recommendations by Organization Size

### Startup (1-5 developers, <10 repos)
**Use:** Centralized Hub
**Why:** Simple, cheap, easy to change later
**Risk:** Low

### Small Company (5-20 developers, 10-30 repos)
**Use:** Centralized Hub
**Why:** Still manageable, good cost/benefit
**Risk:** Low
**Monitor:** Disk usage monthly

### Medium Company (20-50 developers, 30-100 repos)
**Use:** Queue-Based Hub or Per-Repo
**Why:** Centralized hub will struggle
**Risk:** Medium
**Monitor:** Queue depth, worker utilization

### Large Company (50+ developers, 100+ repos)
**Use:** Per-Repo Webhooks
**Why:** Need isolation and scale
**Risk:** High if using centralized
**Monitor:** Per-repo metrics

## Summary

**Current Architecture (Centralized Hub) is perfect for:**
- Your current scale (likely <30 repos)
- Learning and iterating quickly
- Small team with limited resources
- Moderate webhook frequency

**Monitor these metrics to know when to migrate:**
- Disk usage (alert at >60GB)
- Webhook frequency (alert at >15/hour)
- Response times (alert at >20 seconds)
- Cleanup frequency (weekly = yellow, daily = red)

**You're good for now, but plan ahead:**
- Set up monitoring alerts
- Run cleanup script weekly
- Review growth quarterly
- Be ready to migrate when thresholds hit

---

**Last Updated:** 2025-11-06
**Next Review:** 2026-02-06 (Quarterly)
