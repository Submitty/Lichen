#ifndef LICHEN_CONFIG_H
#define LICHEN_CONFIG_H

struct LichenConfig {
    std::string term;
    std::string course;
    std::string gradeable;
    int hash_size;
    int threshold;
    bool provided_code_enabled;
};

#endif
