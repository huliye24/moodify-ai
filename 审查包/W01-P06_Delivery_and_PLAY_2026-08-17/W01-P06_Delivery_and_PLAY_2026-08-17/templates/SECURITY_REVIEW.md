# P06 Security Review

## APK / Source Scan

- [ ] no OSS AccessKey
- [ ] no DB credential
- [ ] no processing API key
- [ ] no private key
- [ ] no long-lived bearer token
- [ ] no production debug endpoint

## Network

- [ ] HTTPS in production
- [ ] signed/proxy token bounded TTL
- [ ] full signed URLs not retained in long-lived logs
- [ ] object bucket not public-read by default

## Authorization

- [ ] READY checked server-side
- [ ] user/access scope checked server-side
- [ ] internal source/stems cannot be guessed/downloaded from client metadata

## Logging

- [ ] no credentials
- [ ] no signed query strings
- [ ] correlation IDs available
