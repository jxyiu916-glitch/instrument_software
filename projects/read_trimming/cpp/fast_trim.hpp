// Fast read trimming with SIMD acceleration
#pragma once

#include <string>
#include <string_view>
#include <vector>
#include <span>
#include <immintrin.h>  // AVX-512

namespace trim {

// SIMD-accelerated quality trimming
class TrimAccelerator {
public:
    // Configure quality threshold
    explicit TrimAccelerator(uint8_t min_quality) : min_quality_(min_quality) {}
    
    // Process a batch of reads with SIMD
    std::vector<std::string_view> 
    trim_batch_simd(std::span<const std::string_view> reads,
                    std::span<const std::string_view> quals) {
        std::vector<std::string_view> results;
        results.reserve(reads.size());
        
        for (size_t i = 0; i < reads.size(); ++i) {
            auto read = reads[i];
            auto qual = quals[i];
            if (read.length() != qual.length()) {
                throw std::invalid_argument("Read and quality lengths must match");
            }
            
            // Find trimming position using SIMD
            size_t trim_pos = find_trim_pos_simd(qual);
            results.push_back(read.substr(0, trim_pos));
        }
        
        return results;
    }
    
    // Try to use hardware acceleration
    bool try_hardware_accel() {
        // Check for AVX-512 support
        #ifdef __AVX512F__
        return true;
        #else
        return false;
        #endif
    }
    
private:
    uint8_t min_quality_;
    
    // Find trimming position using AVX-512
    size_t find_trim_pos_simd(std::string_view qual) {
        #ifdef __AVX512F__
        // Process 64 bases at a time
        const size_t vec_size = 64;
        size_t pos = 0;
        
        // Broadcast min quality to vector
        __m512i min_qual_vec = _mm512_set1_epi8(min_quality_);
        
        while (pos + vec_size <= qual.length()) {
            // Load 64 quality scores
            __m512i qual_vec = _mm512_loadu_si512(
                reinterpret_cast<const __m512i*>(qual.data() + pos)
            );
            
            // Compare with minimum (create mask)
            __mmask64 mask = _mm512_cmpgt_epi8_mask(qual_vec, min_qual_vec);
            
            // Find first failing position
            if (mask != 0xFFFFFFFFFFFFFFFF) {
                // Count trailing ones to find first zero
                unsigned long idx;
                _BitScanForward64(&idx, ~mask);
                return pos + idx;
            }
            
            pos += vec_size;
        }
        #endif
        
        // Fallback: process remaining bases scalar
        for (; pos < qual.length(); ++pos) {
            if (qual[pos] < min_quality_) {
                return pos;
            }
        }
        
        return qual.length();
    }
};

} // namespace trim