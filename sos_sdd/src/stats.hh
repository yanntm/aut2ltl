// C1 instrumentation: every engine operation reports one flat JSON record
// through a Stats sink (the JSONL stream of the IO contract). Records are
// emitted as they are produced, so an aborted run keeps its prefix.
//
// Node figures are unique-table-wide (they include relation diagrams and
// cache survivors), sampled at operation close after an optional garbage
// collection — `table_peak` is libDDD's high-water mark, refreshed on GC.
// Per-set figures (a working set's own node count) are the caller's to
// add via Op::rec() before close.

#pragma once

#include <chrono>
#include <functional>
#include <sstream>
#include <string>
#include <utility>
#include <vector>

#include "ddd/DDD.h"
#include "ddd/MemoryManager.h"

namespace sossdd {

// A flat JSON object builder: string / integer / floating / boolean
// values, insertion order preserved, no nesting.
class Record {
public:
  explicit Record(const std::string &ev) { add("ev", ev); }

  Record &add(const std::string &k, const std::string &v) {
    kv_.emplace_back(k, quote(v));
    return *this;
  }
  Record &add(const std::string &k, const char *v) { return add(k, std::string(v)); }
  Record &add(const std::string &k, long long v) {
    kv_.emplace_back(k, std::to_string(v));
    return *this;
  }
  Record &add(const std::string &k, unsigned long long v) {
    kv_.emplace_back(k, std::to_string(v));
    return *this;
  }
  Record &add(const std::string &k, double v) {
    std::ostringstream o;
    o << v;
    kv_.emplace_back(k, o.str());
    return *this;
  }
  Record &add(const std::string &k, bool v) {
    kv_.emplace_back(k, v ? "true" : "false");
    return *this;
  }

  std::string json() const {
    std::string s = "{";
    for (size_t i = 0; i < kv_.size(); ++i) {
      if (i) s += ",";
      s += quote(kv_[i].first) + ":" + kv_[i].second;
    }
    return s + "}";
  }

private:
  static std::string quote(const std::string &v) {
    std::string s = "\"";
    for (char c : v) {
      if (c == '"' || c == '\\') s += '\\';
      s += c;
    }
    return s + "\"";
  }
  std::vector<std::pair<std::string, std::string>> kv_;
};

// The record sink. A default-constructed Stats is disabled: brackets and
// emits cost near nothing. `gc_per_op` trades time for exact table peaks
// (collection refreshes the high-water mark at every operation close).
class Stats {
public:
  using Sink = std::function<void(const std::string &)>;

  Stats() = default;
  Stats(Sink sink, bool gc_per_op) : sink_(std::move(sink)), gc_per_op_(gc_per_op) {}

  bool enabled() const { return static_cast<bool>(sink_); }
  bool gc_per_op() const { return gc_per_op_; }

  void emit(const Record &r) {
    if (sink_) sink_(r.json());
  }

  // RAII bracket around one engine operation: wall time plus unique-table
  // size before/after and peak. Extra fields go through rec() before the
  // bracket closes (destruction or explicit close()).
  class Op {
  public:
    Op(Stats &s, int phase, const std::string &name)
        : stats_(&s), rec_("op"), t0_(std::chrono::steady_clock::now()) {
      rec_.add("phase", static_cast<long long>(phase)).add("op", name);
      if (stats_->enabled())
        table_before_ = GDDD::statistics();
    }
    Op(const Op &) = delete;
    Op &operator=(const Op &) = delete;
    ~Op() { close(); }

    Record &rec() { return rec_; }

    void close() {
      if (closed_) return;
      closed_ = true;
      if (!stats_->enabled()) return;
      if (stats_->gc_per_op()) MemoryManager::garbage();
      std::chrono::duration<double, std::milli> dt =
          std::chrono::steady_clock::now() - t0_;
      rec_.add("ms", dt.count())
          .add("table_before", static_cast<unsigned long long>(table_before_))
          .add("table_after", static_cast<unsigned long long>(GDDD::statistics()))
          .add("table_peak", static_cast<unsigned long long>(GDDD::peak()));
      stats_->emit(rec_);
    }

  private:
    Stats *stats_;
    Record rec_;
    std::chrono::steady_clock::time_point t0_;
    size_t table_before_ = 0;
    bool closed_ = false;
  };

  Op op(int phase, const std::string &name) { return Op(*this, phase, name); }

private:
  Sink sink_;
  bool gc_per_op_ = false;
};

}  // namespace sossdd
