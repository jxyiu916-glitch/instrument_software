// Fast UMI deduplication and clustering using modern C++
#pragma once

#include <string>
#include <string_view>
#include <vector>
#include <unordered_map>
#include <span>
#include <memory>
#include <algorithm>
#include <cassert>

namespace umi {

// RAII wrapper for UMI data
template<typename StringType>
class UMIData {
public:
    explicit UMIData(std::vector<StringType> umis)
        : umis_(std::move(umis)) {}
    
    // Move semantics
    UMIData(UMIData&&) noexcept = default;
    UMIData& operator=(UMIData&&) noexcept = default;
    
    // No copying (RAII)
    UMIData(const UMIData&) = delete;
    UMIData& operator=(const UMIData&) = delete;
    
    const std::vector<StringType>& umis() const { return umis_; }
    
private:
    std::vector<StringType> umis_;
};

// Compute Hamming distance between two strings
template<typename StringView>
size_t hamming_distance(StringView a, StringView b) {
    if (a.length() != b.length()) {
        throw std::invalid_argument("Sequences must be same length");
    }
    return std::inner_product(
        a.begin(), a.end(), b.begin(), 0,
        std::plus<>(),
        std::not_equal_to<>()
    );
}

// UMI clustering with configurable distance metric
template<typename StringView>
class UMIClusterer {
public:
    explicit UMIClusterer(size_t max_distance) : max_dist_(max_distance) {}
    
    // Move semantics
    UMIClusterer(UMIClusterer&&) noexcept = default;
    UMIClusterer& operator=(UMIClusterer&&) noexcept = default;
    
    // No copying (stateful)
    UMIClusterer(const UMIClusterer&) = delete;
    UMIClusterer& operator=(const UMIClusterer&) = delete;
    
    // Cluster UMIs within max_distance
    std::vector<std::vector<StringView>>
    cluster(std::span<const StringView> umis) const {
        std::vector<std::vector<StringView>> clusters;
        std::vector<bool> assigned(umis.size(), false);
        
        for (size_t i = 0; i < umis.size(); ++i) {
            if (assigned[i]) continue;
            
            std::vector<StringView> cluster;
            cluster.push_back(umis[i]);
            assigned[i] = true;
            
            for (size_t j = i + 1; j < umis.size(); ++j) {
                if (assigned[j]) continue;
                if (hamming_distance(umis[i], umis[j]) <= max_dist_) {
                    cluster.push_back(umis[j]);
                    assigned[j] = true;
                }
            }
            
            clusters.push_back(std::move(cluster));
        }
        
        return clusters;
    }
    
private:
    size_t max_dist_;
};

// Count unique UMIs with optional clustering
template<typename StringView>
class UMICounter {
public:
    explicit UMICounter(size_t max_distance = 0)
        : clusterer_(max_distance > 0 ? std::make_unique<UMIClusterer<StringView>>(max_distance)
                                    : nullptr) {}
    
    // Move semantics
    UMICounter(UMICounter&&) noexcept = default;
    UMICounter& operator=(UMICounter&&) noexcept = default;
    
    std::unordered_map<StringView, size_t>
    count_umis(std::span<const StringView> umis) const {
        if (!clusterer_) {
            return count_exact(umis);
        }
        return count_clustered(umis);
    }
    
private:
    std::unique_ptr<UMIClusterer<StringView>> clusterer_;
    
    std::unordered_map<StringView, size_t>
    count_exact(std::span<const StringView> umis) const {
        std::unordered_map<StringView, size_t> counts;
        for (const auto& umi : umis) {
            ++counts[umi];
        }
        return counts;
    }
    
    std::unordered_map<StringView, size_t>
    count_clustered(std::span<const StringView> umis) const {
        assert(clusterer_);
        auto clusters = clusterer_->cluster(umis);
        
        std::unordered_map<StringView, size_t> counts;
        for (const auto& cluster : clusters) {
            if (!cluster.empty()) {
                counts[cluster[0]] = cluster.size();
            }
        }
        return counts;
    }
};

} // namespace umi