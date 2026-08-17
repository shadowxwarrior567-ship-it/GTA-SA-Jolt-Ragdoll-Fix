LOCAL_PATH := $(call my-dir)

include $(CLEAR_VARS)

LOCAL_MODULE := gtasa_jolt_fix
LOCAL_SRC_FILES := main.cpp

LOCAL_CPPFLAGS := -std=c++17 -fno-exceptions -fno-rtti -fvisibility=hidden
LOCAL_CFLAGS := -ffunction-sections -fdata-sections

LOCAL_LDFLAGS := -Wl,--gc-sections

LOCAL_LDLIBS := -llog -ldl -landroid

include $(BUILD_SHARED_LIBRARY)
