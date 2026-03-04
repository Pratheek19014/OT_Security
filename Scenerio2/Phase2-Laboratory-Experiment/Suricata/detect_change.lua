function init (args)
    local needs = {}
    needs["payload"] = tostring(true)
    return needs
end

-- Table to store state: {last_val, count, start_time}
local ip_stats = {}

function match(args)
    local payload = args["payload"]
    local src_ip = tostring(args["ipver"] == 4 and args["saddr"] or "unknown")
    local current_time = os.time()

    -- 1. Check for S7 Job (0x32 0x01)
    if not string.find(payload, "\x32\x01") then
        return 0
    end

    -- 2. Look for the S7 Data Marker from your Wireshark hex
    local marker = "\x00\x04\x00\x20\x01\x00"
    local pos = string.find(payload, marker)
    if not pos then return 0 end

    -- 3. Extract speed (Big Endian)
    local speed_offset = pos + 6
    if #payload < speed_offset + 1 then return 0 end
    
    local speed_high = string.byte(payload, speed_offset)
    local speed_low = string.byte(payload, speed_offset + 1)
    local current_speed = (speed_high * 256) + speed_low

    -- 4. Initialize or reset tracker if 10 seconds have passed
    if not ip_stats[src_ip] or (current_time - ip_stats[src_ip].start_time) > 10 then
        ip_stats[src_ip] = {last_val = current_speed, count = 0, start_time = current_time}
        return 0
    end

    -- 5. Calculate change
    local diff = math.abs(current_speed - ip_stats[src_ip].last_val)
    ip_stats[src_ip].last_val = current_speed

    -- 6. If speed jump > 100, increment counter
    if diff > 100 then
        ip_stats[src_ip].count = ip_stats[src_ip].count + 1
    end

    -- 7. Trigger only if we hit 3 changes within the 10s window
    if ip_stats[src_ip].count >= 3 then
        -- Reset after trigger to avoid continuous alerts
        ip_stats[src_ip].count = 0 
        return 1
    end

    return 0
end
