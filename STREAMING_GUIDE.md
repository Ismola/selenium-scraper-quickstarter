# 🎥 Selenium Scraper Streaming Guide

## Overview

This selenium-scraper-quickstarter now includes **automatic browser streaming capabilities** that allow you to record and monitor your web automation tasks in real-time. The streaming system is seamlessly integrated into the existing workflow.

## ✨ Features

- **🚀 Automatic Streaming**: Starts automatically when you call any endpoint that uses the browser
- **📁 File Recording**: Saves MP4 videos of your automation sessions
- **🔧 Simple Integration**: Works with existing endpoints without code changes
- **⚙️ Configurable**: Adjust FPS, resolution, and output location
- **🛡️ Production Ready**: Disabled by default, enable when needed

## 🚀 Quick Start

### 1. Enable Streaming

Set the environment variable:

```bash
export STREAMING_ENABLED=true
```

Or add to your `.env` file:

```
STREAMING_ENABLED=true
```

### 2. Use Any Endpoint

Simply call your existing endpoints normally:

```bash
curl -X GET \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer sample" \
  -d '{"username":"test","password":"test"}' \
  http://localhost:3000/sample
```

### 3. Monitor Streaming

Check streaming status:

```bash
curl -H "Authorization: Bearer sample" \
  http://localhost:3000/stream/status
```

Response:

```json
{
  "streaming": true,
  "output_file": "/tmp/current_session.mp4",
  "protocol": "file"
}
```

### 4. Stop Streaming

Manually stop when needed:

```bash
curl -X POST \
  -H "Authorization: Bearer sample" \
  http://localhost:3000/stream/stop
```

## 📚 API Endpoints

### Streaming Control

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/stream/status` | GET | Get current streaming status |
| `/stream/stop` | POST | Stop current streaming session |

### Streaming Status Response

```json
{
  "streaming": true,
  "output_file": "/tmp/current_session.mp4",
  "protocol": "file"
}
```

## ⚙️ Configuration

Configure via environment variables:

```bash
# Enable/disable streaming
STREAMING_ENABLED=true

# Video settings
STREAMING_FPS=10                    # Frames per second
STREAMING_WIDTH=1280                # Video width
STREAMING_HEIGHT=720                # Video height
STREAMING_QUALITY=80                # Video quality (1-100)
```

### Configuration Options

| Variable | Default | Description |
|----------|---------|-------------|
| `STREAMING_ENABLED` | `false` | Enable automatic streaming |
| `STREAMING_FPS` | `10` | Frames per second for recording |
| `STREAMING_WIDTH` | `1280` | Video width in pixels |
| `STREAMING_HEIGHT` | `720` | Video height in pixels |
| `STREAMING_QUALITY` | `80` | Video quality percentage |

## 📁 Output Files

- **Default Location**: `/tmp/current_session.mp4`
- **Format**: MP4 (H.264 codec)
- **Automatic Naming**: Files are overwritten for each new session
- **Custom Location**: Configure via environment variables (coming soon)

## 🔧 How It Works

### Automatic Integration

The streaming system automatically:

1. **Detects Browser Usage**: When any endpoint uses `get_page()`
2. **Starts Recording**: Begins capturing browser frames
3. **Records Actions**: Captures all navigation, clicks, typing, etc.
4. **Saves Video**: Writes MP4 file during the session
5. **Continues Between Calls**: Stays active across multiple endpoint calls

### Architecture

```
┌─────────────────┐    ┌──────────────┐    ┌─────────────────┐
│   Your Endpoint │───▶│  WebDriver   │───▶│ Streaming       │
│   (/sample)     │    │  (Browser)   │    │ Service         │
└─────────────────┘    └──────────────┘    └─────────────────┘
                                                    │
                                                    ▼
                                           ┌─────────────────┐
                                           │  MP4 Video      │
                                           │  Output         │
                                           └─────────────────┘
```

## 🎯 Use Cases

### Development & Debugging

- **Visual Debugging**: See exactly what your automation is doing
- **Bug Reproduction**: Record sessions that fail for analysis
- **Demo Creation**: Generate videos of your automation workflows

### Testing & QA

- **Test Documentation**: Visual proof of test execution
- **Regression Testing**: Compare video outputs across versions
- **User Acceptance**: Show stakeholders how automation works

### Production Monitoring

- **Session Recording**: Keep records of important automation runs
- **Compliance**: Video evidence for audit trails
- **Training**: Create training materials from real sessions

## 🛠️ Advanced Usage

### Environment-Specific Configuration

**Development** (`.env.development`):

```bash
STREAMING_ENABLED=true
STREAMING_FPS=15
STREAMING_QUALITY=70
```

**Production** (`.env.production`):

```bash
STREAMING_ENABLED=false
# Streaming disabled by default in production
```

### Docker Integration

Add to your `Dockerfile`:

```dockerfile
# Install FFmpeg for streaming
RUN apt-get update && apt-get install -y ffmpeg

# Set streaming environment
ENV STREAMING_ENABLED=true
ENV STREAMING_FPS=10
```

### Custom Controllers

Your existing controllers work automatically:

```python
def my_custom_controller(data):
    # This will automatically be streamed if enabled
    driver = get_page()
    
    # Your automation logic here
    driver.get("https://example.com")
    # ... more actions ...
    
    close_driver(driver)  # Streaming continues
    return "success"
```

## 🚨 Production Considerations

### Performance Impact

- **CPU Usage**: +10-15% for video encoding
- **Memory**: +50-100MB for frame buffering
- **Disk Space**: ~1-5MB per minute of video

### Security

- **Sensitive Data**: Videos may contain sensitive information
- **Access Control**: Ensure proper file permissions on output directory
- **Cleanup**: Implement video file rotation/cleanup policies

### Recommended Settings

**Development**:

```bash
STREAMING_ENABLED=true
STREAMING_FPS=15
STREAMING_QUALITY=80
```

**Production** (when needed):

```bash
STREAMING_ENABLED=true
STREAMING_FPS=8
STREAMING_QUALITY=60
```

## 🐛 Troubleshooting

### Common Issues

**Streaming not starting**:

```bash
# Check if enabled
curl http://localhost:3000/stream/status

# Check logs for errors
tail -f logs/app.log
```

**No video output**:

- Ensure FFmpeg is installed: `ffmpeg -version`
- Check write permissions on output directory
- Verify browser is actually opening (not headless when streaming)

**Performance issues**:

- Reduce FPS: `STREAMING_FPS=5`
- Lower quality: `STREAMING_QUALITY=50`
- Reduce resolution: `STREAMING_WIDTH=800 STREAMING_HEIGHT=600`

### Debug Mode

Enable detailed logging:

```bash
export LOG_LEVEL=DEBUG
export STREAMING_DEBUG=true
```

## 📋 Best Practices

1. **Enable Only When Needed**: Keep disabled in production unless required
2. **Monitor Disk Space**: Implement cleanup for old video files
3. **Secure Output**: Protect video files containing sensitive data
4. **Performance Testing**: Test with streaming enabled before production
5. **Backup Strategy**: Include video files in backup considerations

## 🔄 Migration from Previous Versions

If upgrading from a version without streaming:

1. **Environment Variables**: Add streaming config to `.env`
2. **Dependencies**: Ensure FFmpeg is installed
3. **No Code Changes**: Existing endpoints work automatically
4. **Testing**: Verify streaming with your existing controllers

## 📞 Support

For issues related to streaming:

1. Check streaming status endpoint
2. Review application logs
3. Verify FFmpeg installation
4. Check file permissions on output directory

---

**Note**: Streaming is designed to be completely transparent to your existing automation logic. Enable it when you need visual monitoring, disable it for pure automation performance.
