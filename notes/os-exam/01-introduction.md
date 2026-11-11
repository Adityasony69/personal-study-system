# Introduction to operating systems

## What an operating system is
An operating system (OS) is the software that sits between the hardware and the programs you run. It has two jobs:

- **Resource manager:** decides who gets the CPU, memory, disk and devices, and when.
- **Extended machine:** hides ugly hardware details behind simple ideas such as files, processes and windows.

Without an OS every program would need its own code to drive the disk, the keyboard and the screen.

```
   Users
     |
 Application programs   (browser, editor, compiler)
     |
 System calls
     |
 Operating system       (kernel)
     |
 Hardware               (CPU, memory, disk, devices)
```

## Goals
- **Convenience:** easy for users and programmers.
- **Efficiency:** keep the hardware busy doing useful work.
- **Ability to evolve:** new features without breaking old programs.

## Types of operating systems
| Type | Idea | Example or use |
|---|---|---|
| Batch | Jobs are collected and run one after another with no user interaction | Early mainframes, payroll runs |
| Multiprogramming | Several jobs in memory; when one waits for I/O the CPU switches to another | Keeps CPU utilisation high |
| Multitasking (time sharing) | CPU switches between jobs so fast that each user feels alone on the machine | Windows, Linux, macOS |
| Multiprocessing | Two or more CPUs share the work | Servers, modern laptops |
| Distributed | Many machines appear as one system | Cluster and cloud systems |
| Real-time | Results must arrive within a deadline | Hard: airbags, pacemakers. Soft: video streaming |
| Network | Machines know about each other and share files and printers | Windows Server |
| Mobile and embedded | Small memory, battery aware, touch input | Android, iOS, router firmware |

**Multiprogramming versus multitasking:** multiprogramming switches only when a job waits for I/O (goal: CPU utilisation). Multitasking also switches on a timer (goal: quick response).

**Symmetric versus asymmetric multiprocessing:** in symmetric (SMP) every CPU is equal and runs the OS. In asymmetric, one master CPU hands work to the others.

## System components
- **Process management:** create, schedule, stop and synchronise processes.
- **Main memory management:** track which parts of memory are used and by whom.
- **File management:** create, delete, read, write files and directories.
- **I/O system management:** device drivers, buffering, caching, spooling.
- **Secondary storage management:** free space, allocation, disk scheduling.
- **Protection and security:** control who can access what.
- **Networking:** communication between machines.
- **Command interpreter (shell):** reads commands and runs them.

## Operating system services
Services for the user:

- User interface (command line or graphical)
- Program execution: load a program and run it
- I/O operations
- File system manipulation
- Communication between processes
- Error detection

Services for the system itself:

- Resource allocation
- Accounting: who used how much
- Protection and security

## Kernel mode and user mode
The CPU has a mode bit.

- **User mode:** normal programs. Dangerous instructions such as direct I/O are forbidden.
- **Kernel mode:** the OS. Everything is allowed.

A program moves into kernel mode only through a system call, an interrupt or a trap. This is called **dual-mode operation** and it protects the OS from buggy or malicious programs.

## System calls
A system call is how a program asks the OS to do something it is not allowed to do itself.

What happens on a call such as `read`:

1. The program puts the call number and arguments in registers.
2. It runs a trap instruction. The CPU switches to kernel mode.
3. The kernel looks up the call number in the system call table and runs the handler.
4. The result is put in a register and the CPU returns to user mode.

| Category | What it does | Linux examples | Windows examples |
|---|---|---|---|
| Process control | Create, end, wait | `fork`, `exec`, `exit`, `wait` | `CreateProcess`, `ExitProcess` |
| File management | Open, read, write, close | `open`, `read`, `write`, `close` | `CreateFile`, `ReadFile`, `WriteFile` |
| Device management | Request and release devices | `ioctl`, `read`, `write` | `SetConsoleMode` |
| Information | Time, process id, system data | `getpid`, `time` | `GetCurrentProcessID` |
| Communication | Pipes, shared memory, sockets | `pipe`, `shmget`, `socket` | `CreatePipe` |
| Protection | Permissions | `chmod`, `chown` | `SetFileSecurity` |

## Kernel structures
| Structure | Idea | Good | Bad |
|---|---|---|---|
| Monolithic | The whole OS runs as one big program in kernel mode | Fast | One bug can crash everything (Linux is monolithic with loadable modules) |
| Layered | OS built in layers, each using only the one below | Easy to debug | Slow, hard to define layers |
| Microkernel | Only the essentials in the kernel; the rest runs as user programs | Reliable, easy to extend | Slower because of message passing (Mach, QNX) |
| Hybrid | A mix | Practical | Windows and macOS |

## Interrupts
An interrupt is a signal that makes the CPU stop what it is doing and run OS code. Hardware interrupts come from devices (key pressed, disk finished). Software interrupts (traps) come from programs: a system call or an error such as divide by zero.

## Booting in short
Power on, firmware (BIOS or UEFI) tests the hardware, the bootloader loads the kernel into memory, the kernel starts the first process, and that process starts the rest.

## Exam points
- OS = resource manager + interface between user and hardware.
- A system call switches from user mode to kernel mode.
- Multiprogramming raises CPU utilisation; time sharing lowers response time.
- Hard real-time systems must never miss a deadline.
- `fork` creates a process; `exec` replaces its program.

## Check yourself
- What two roles does an OS play?
- Why does the CPU need two modes?
- How is multitasking different from multiprogramming?
- Give one system call from each of four categories.
