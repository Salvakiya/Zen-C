// compat.h - Compatibility layer for different platforms and compilers
#ifndef ZC_COMPAT_H
#define ZC_COMPAT_H

#include <stddef.h>
#include <stddef.h>
#include <stdbool.h>
#include <stdio.h>


#ifdef __cplusplus
extern "C" {
#endif

#if defined(__clang__)
    #define ZC_COMPILER_CLANG
#elif defined(__GNUC__) || defined(__GNUG__)
    #define ZC_COMPILER_GCC 
#elif defined(_MSC_VER)
    #define ZC_COMPILER_MSVC
#elif defined(__TINYC__)
    #define ZC_COMPILER_TINYC
#elif defined(__ZIG__)
    #define ZC_COMPILER_ZIG
#else
    #define ZC_COMPILER_UNKNOWN
#endif

#if defined(ZC_COMPILER_TINYC) || defined(ZC_COMPILER_MSVC)
#define __auto_type __typeof__
#endif

/* --- Platform Detection & Base Headers --- */
#if defined(_WIN32) || defined (_WIN64)
#   define ZC_ON_WINDOWS
#   define WIN32_LEAN_AND_MEAN
#   define NOMINMAX
#   include <windows.h>
#   include <winnetwk.h>
#   include <time.h>
#   include <fcntl.h>

    typedef HMODULE zc_dlhandle;
#else
#   define ZC_ON_POSIX
#   include <unistd.h>
#   include <pthread.h>
#   include <semaphore.h>
#   include <sys/stat.h>
#   include <time.h>

#   include <dlfcn.h>
#   include <termios.h>

    typedef void* zc_dlhandle;
#endif

int zc_getpid();
zc_dlhandle zc_dlopen(const char *path);
void *zc_dlsym(zc_dlhandle handle, const char *symbol);
void zc_dlclose(zc_dlhandle handle);


#ifdef __cplusplus
}
#endif

#endif // ZC_COMPAT_H

// compat.h - implementation
#ifdef ZC_COMPAT_IMPLEMENTATION
#undef ZC_COMPAT_IMPLEMENTATION

int zc_getpid(void){
#ifdef ZC_ON_WINDOWS
    return (int)GetCurrentProcessId();
#else
    return (int)getpid();
#endif
}

zc_dlhandle zc_dlopen(const char *path)
{
#ifdef ZC_ON_WINDOWS
    return LoadLibraryA(path);
#else
    return dlopen(path, RTLD_LAZY);
#endif
}

void zc_dlclose(zc_dlhandle handle)
{
#ifdef ZC_ON_WINDOWS
    if (handle)
    {
        FreeLibrary(handle);
    }
#else
    if (handle)
    {
        dlclose(handle);
    }
#endif
}

void *zc_dlsym(zc_dlhandle handle, const char *symbol)
{
#ifdef ZC_ON_WINDOWS
    return (void *)GetProcAddress(handle, symbol);
#else
    return dlsym(handle, symbol);
#endif
}


#endif // ZC_COMPAT_IMPLEMENTATION