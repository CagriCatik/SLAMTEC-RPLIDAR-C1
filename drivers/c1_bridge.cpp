// Own adapter to SLAMTEC's public SDK. No vendor demo source is incorporated.
#include "sl_lidar.h"
#include "sl_lidar_driver.h"
#include <chrono>
#include <csignal>
#include <cstring>
#include <iomanip>
#include <iostream>
#include <memory>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

static volatile std::sig_atomic_t interrupted = 0;
static void interrupt_handler(int) { interrupted = 1; }
static double clock_s() {
    return std::chrono::duration<double>(std::chrono::steady_clock::now().time_since_epoch()).count();
}
static void check(sl_result result, const char* operation) {
    if (SL_IS_FAIL(result)) {
        std::ostringstream message; message << operation << " failed: 0x" << std::hex << result;
        throw std::runtime_error(message.str());
    }
}
static std::string quoted(const std::string& input) {
    std::ostringstream out; out << '"';
    for (unsigned char c : input) {
        if (c == '"' || c == '\\') out << '\\' << c;
        else if (c < 32) out << "\\u" << std::hex << std::setw(4) << std::setfill('0') << unsigned(c) << std::dec;
        else out << c;
    }
    out << '"'; return out.str();
}
struct Device {
    std::unique_ptr<sl::IChannel> channel;
    std::unique_ptr<sl::ILidarDriver> driver;
    bool motor_started = false;
    ~Device() {
        if (driver) {
            if (motor_started) { driver->stop(); driver->setMotorSpeed(0); }
            driver->disconnect();
        }
    }
};
int main(int argc, char** argv) {
    try {
        if (argc < 2) {
            std::cerr << "Usage: c1_bridge PORT [--inspect] [--scans N] [--mode ID] [--baud N]\n";
            return 2;
        }
        std::string port = argv[1]; bool inspect = false;
        int scans = 30, baud = 460800, mode_id = -1;
        for (int i = 2; i < argc; ++i) {
            std::string option = argv[i];
            if (option == "--inspect") inspect = true;
            else if (i+1 < argc && option == "--scans") scans = std::stoi(argv[++i]);
            else if (i+1 < argc && option == "--mode") mode_id = std::stoi(argv[++i]);
            else if (i+1 < argc && option == "--baud") baud = std::stoi(argv[++i]);
            else throw std::runtime_error("Unknown/missing bridge argument");
        }
        if (scans < 1 || baud < 1 || mode_id > 65535 || mode_id < -1) throw std::runtime_error("Invalid bridge limits");
        std::signal(SIGINT, interrupt_handler); std::signal(SIGTERM, interrupt_handler);
        std::signal(SIGPIPE, SIG_IGN);
        std::cout.exceptions(std::ios::badbit | std::ios::failbit);
        Device device;
        auto channel = sl::createSerialPortChannel(port, baud);
        check(channel.err, "create channel"); device.channel.reset(*channel);
        auto driver = sl::createLidarDriver();
        check(driver.err, "create driver"); device.driver.reset(*driver);
        check(device.driver->connect(device.channel.get()), "connect");
        sl_lidar_response_device_info_t info{};
        sl_lidar_response_device_health_t health{};
        check(device.driver->getDeviceInfo(info), "device info");
        check(device.driver->getHealth(health), "health");
        std::vector<sl::LidarScanMode> modes;
        check(device.driver->getAllSupportedScanModes(modes), "scan modes");
        std::ostringstream serial;
        for (unsigned char value : info.serialnum) serial << std::hex << std::setw(2) << std::setfill('0') << unsigned(value);
        std::string model_name;
        auto model_result = device.driver->getModelNameDescriptionString(model_name, true, &info);
        if (SL_IS_FAIL(model_result)) model_name = "unavailable";
        std::cout << "{\"type\":\"info\",\"bridge_schema\":1,\"model_code\":" << unsigned(info.model)
                  << ",\"model_name\":" << quoted(model_name) << ",\"firmware\":" << info.firmware_version
                  << ",\"hardware\":" << unsigned(info.hardware_version) << ",\"serial\":" << quoted(serial.str())
                  << ",\"health\":" << unsigned(health.status) << ",\"health_error\":" << health.error_code << ",\"modes\":[";
        bool first = true;
        for (const auto& mode : modes) {
            if (!first) std::cout << ',';
            first = false;
            std::cout << "{\"id\":" << mode.id << ",\"name\":" << quoted(std::string(mode.scan_mode, strnlen(mode.scan_mode, 64)))
                      << ",\"us_per_sample\":" << mode.us_per_sample << ",\"max_distance_m\":" << mode.max_distance << '}';
        }
        std::cout << "]}" << std::endl;
        if (inspect) return 0;
        if (health.status != 0) throw std::runtime_error("Refusing scan: device health is not healthy");
        if (model_name == "unavailable" || model_name.find("C1") == std::string::npos)
            throw std::runtime_error("Refusing scan: model description does not identify C1; verify device/SDK");
        if (mode_id >= 0) {
            bool found = false;
            for (const auto& mode : modes) if (mode.id == mode_id) found = true;
            if (!found) throw std::runtime_error("Requested scan mode not advertised");
        }
        if (interrupted) return 0;
        device.motor_started = true; // attempt cleanup even if the motor command fails ambiguously
        check(device.driver->setMotorSpeed(), "start motor");
        sl::LidarScanMode selected{};
        if (mode_id < 0) check(device.driver->startScan(false, true, 0, &selected), "start typical scan");
        else check(device.driver->startScanExpress(false, sl_u16(mode_id), 0, &selected), "start selected scan");
        for (int sequence = 0; sequence < scans && !interrupted; ++sequence) {
            sl_lidar_response_measurement_node_hq_t nodes[8192]; size_t count = 8192;
            const double begin = clock_s();
            auto result = device.driver->grabScanDataHq(nodes, count, 1000);
            if (interrupted) break;
            check(result, "grab scan");
            const double end = clock_s();
            std::cout << std::setprecision(15) << "{\"type\":\"scan\",\"bridge_schema\":1,\"sequence\":" << sequence
                      << ",\"time_s\":" << end << ",\"host_receive_duration_s\":" << end-begin
                      << ",\"scan_mode_id\":" << selected.id << ",\"max_distance_m\":" << selected.max_distance;
            auto array = [&](const char* name, auto value) {
                std::cout << ",\"" << name << "\":[";
                for (size_t i=0; i<count; ++i) { if(i) std::cout << ','; std::cout << value(nodes[i]); }
                std::cout << ']';
            };
            array("angle_q14", [](const auto& n){return unsigned(n.angle_z_q14);});
            array("distance_q2", [](const auto& n){return n.dist_mm_q2;});
            array("quality", [](const auto& n){return unsigned(n.quality);});
            array("flags", [](const auto& n){return unsigned(n.flag);});
            std::cout << '}' << std::endl;
        }
        return 0;
    } catch (const std::exception& error) { std::cerr << error.what() << '\n'; return 2; }
}
