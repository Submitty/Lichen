#ifndef LICHEN_CONFIG_H
#define LICHEN_CONFIG_H

struct LichenConfig {
    std::string semester;
    std::string course;
    std::string gradeable;
    int sequence_length;
    int threshold;
    bool provided_code_enabled;
};

#endif
