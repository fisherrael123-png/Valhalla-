# Valhalla 教程04

> 适合对象：完成了 Valhalla  教程01、02、03 的使用者，了解Valhalla的知识库系统的五层架构概念以及它们的实现
>
> 学习目标：了解知识库操作系统的架构
>
> 预计时间：30-40 分钟

## 知识库系统和知识库操作系统的关系

Valhalla的知识库系统和知识库操作系统借鉴了数据库系统和数据库管理系统的概念。

但需要注意的是：`Valhalla绝不只是一个知识库，知识库只是它的一部分，Valhalla是一个AI综合工作环境`

注意分清两个概念：

- 知识库系统是对知识库进行组织的文件系统。
- 知识库操作系统是使用知识库系统的操作系统。

作个类比，知识库系统是你的个人计算机的硬盘，知识库是你的硬盘的各个分区，如c盘，d盘，e盘。知识库操作系统则是windows、linux。
一般的`个人知识库`就像一个只会管理存储文件的数据库系统，而Valhalla是一个会使用这些文件进行办公、娱乐的操作系统。

## 操作系统的内核架构简介

在操作系统设计中，内核负责维持系统运行所需的基本能力，例如进程管理、内存管理、权限控制、设备访问和系统调用等。围绕内核如何组织系统功能，通常可以区分出`宏内核`、`微内核`和`混合内核`等不同架构思想。

`宏内核`倾向于将大量系统功能放在内核内部，使系统调用路径较短、执行效率较高，但也容易导致内核规模庞大、模块之间耦合较强。

`微内核`则尽量缩小内核规模，只在内核中保留最基本的调度、通信和权限机制，将文件系统、驱动、网络等功能移到用户态服务中运行。这种方式模块边界清晰、可维护性较好，但服务之间通信和调度成本可能更高。

`混合内核`可以理解为二者之间的折中。它并不追求把所有功能都放入内核，也不把所有服务都彻底移出内核，而是根据稳定性、性能、权限和维护需求，将核心机制保留在内核中，将可扩展、可替换、面向具体任务的功能组织为系统服务。这样既能保留内核运行秩序和关键控制能力，又能避免系统功能过度集中在一个庞大的核心中。

## Valhalla知识库操作系统的架构

Valhalla知识库操作系统基本上使用了微内核模式。

### 运行时加载模式

微内核的操作系统的特点是，`操作系统内核`常驻内存，系统的其他部分并不在内存中，当需要使用某种功能时，内核将相关操作的程序代码加载到内存中运行，这些临时为特定功能而运行的程序代码一般被称作`系统服务`。

21世纪之后的windows操作系统就使用了这种微内核架构，打开windows的任务管理器，将进程按名称排列，那些被归为`windows进程`的进程，就是`系统服务`。

当Valhalla技能被启动时，`SKILL.md`的内容就会被加载到上下文中，而skill的其他部分只有在其负责的功能被启动时才加载到上下文中执行。

skill的`渐进式披露`和微内核架构系统服务的`按需加载`不谋而合，`SKILL.md`如同`操作系统内核`一样常驻，skill的其他部分`按需加载`，微内核操作系统的系统服务也`按需加载`。

唯一不同的是操作系统的系统服务在结束需求后可以被立即调出内存，将内存空闲出来让其他程序使用，而skill的按需加载则是加载后就始终存在于上下文中，直到重启会话或者压缩上下文。

这导致了一种`LLM的新视角`：将LLM看作一个功能强大的CPU，上下文窗口看作内存，等于是有了一个很好的虚拟的计算机硬件。而Valhalla就作为运行在这套虚拟硬件上的操作系统。

### Valhalla知识库操作系统

#### 操作系统内核

操作系统的内核由该skill下的`SKILL.md`文件实现，它主要实现启动自检、加载路由表、安全约束、prompt路由等基本功能。

`SKILL.md`几乎全部由自然语言构建，除了bootstrap这个启动程序，它主要负责验证系统完整性和加载路由表操作，功能单一且需要稳定执行，因此用python写成。

#### 系统服务

在内核外，Valhalla系统通过构建相互独立的系统服务实现具体的功能。

一个系统服务的标准流程是：prompt输入-->router-->contract-->workflow。

| 发出指令 | 确定启动的系统服务 | 检验当前环境是否可执行 | 执行系统服务 |
| --- | --- | --- | --- |
| prompt输入 | router | contract | workflow |

#### 从router查看系统服务

了解系统服务的最佳办法就是查看router。

如前所述，Valhalla主要由自然语言构建，router也不例外，你可以在Valhalla的skill文件夹下的router子文件夹内找到`router.md`

这是`Valhalla 0.5.10b`版本router的`知识库生命周期`部分的router

这部分系统服务的功能是：`用于当前 root 下知识库的列表、新建、登记、启动、退出、注销和改名。此类操作管理知识库本身，不负责资料语义加工。`

`分类`：该系统服务的类型；

`触发条件`：输入什么样的prompt可以使用该系统服务；

`加载`：该系统服务的入口，加载该入口，开始下面流程。

| 分类 | 触发条件 | 加载 |
| --- | --- | --- |
| `list_root` | 列出当前 root 下的知识库、当前 root 有哪些知识库、知识库列表 | `contract\kb_operation\list_root_contract.yaml` |
| `create_kb` | 新建知识库 | `contract\kb_operation\create_kb_contract.yaml` |
| `register_existing_kb` | 登记已有知识库、注册已有知识库、将已有 Wiki 登记为知识库、登记已有kb | `contract\kb_operation\register_existing_kb_contract.yaml` |
| `start_kb` | 启动或切换知识库 | `contract\kb_operation\start_kb_contract.yaml` |
| `exit_kb` | 退出当前知识库 | `contract\kb_operation\exit_kb_contract.yaml` |
| `remove_kb` | 删除知识库、移除知识库、注销知识库、从当前 root 移除知识库 | `contract\kb_operation\remove_kb_contract.yaml` |
| `rename_kb` | 修改知识库名称、重命名知识库、知识库改名、把知识库<旧名称>改名为<新名称> | `contract\kb_operation\rename_kb_contract.yaml` |

#### 从contract到workflow

`contract`会包含一系列条件验证，以`create_kb_contract.yaml`为例，最主要的包括：

1. 输入验证:

```text
    input:
        required:
        - kb名称
        optional: []
        pattern:
            canonical: 创建kb <kb名称>
            examples:
            - 创建知识库-测试库
            - 创建知识库，名称为测试库
            - 创建kb 测试库
```

主要是确定输入指令中的参数，比如这里的参数为<kb名称>。

2. 读写权限：

```text
   permissions:
      read: true
      write: true
```

3. 风险等级：

```text
risk:
      level: high
      confirmation_required: true
```

risk level分为`low`、`medium`、`high`。

如果是high，`SKILL.md`即内核中的安全规则强制要求确认。

当risk level为low，confirmation_required则提供这种局部性的确认要求。

如果你觉得`摄入`操作老是让你确认很烦，可以把`ingest`还有`register_resource`的risk改成

```text
risk:
      level: low
      confirmation_required: false
```

这样就不用老是让你确认了。

4. 状态要求：

```text
    state_constraints:
      os_status:
        allowed:
        - base
        on_denied: 拒绝执行 create_kb：该操作只能在 base 状态下运行。
      kb_status:
        allowed:
        - idle
        on_denied: 拒绝执行 create_kb：该操作只能在 idle 状态下运行。
```

查看当前状态是否符合该要求。

`os_status`有两种状态：`base`和`admin`，可以通过`进入admin`或`进入管理状态`来使`os_status`进入`admin`，使用`退出admin`或`退出管理状态`来进入`base`。

有的很重要的指令需要慎重，所以放到了admin状态才能使用。

在`codex --yolo`模式下，有时会跳过切换`os_status`操作，自动执行`进入管理状态`操作，但依然需要你的明确确认才能执行。这也是AIOS的特点：它不一定很稳定。

`kb_status`也有两种状态：`idle`和`kb:<kb名称>`，`idle`表示当前没启动任何知识库， `kb:<kb名称>`表示当前启动了名称为<kb名称>的知识库。

可以通过`启动知识库 <kb名称>`，如“启动知识库 测试库”来启动名为“测试库”的知识库。

设置`kb_status`的目的是，将那些针对知识库的操作的目标，设定为当前启动的知识库

5. workflow入口：

```text
executor:
      type: workflow
      paths:
      - workflows/kb/create_kb.md
      load_after_validation: true
```

可以看到，当前面的验证通过之后，Valhalla就加载`workflows/kb/create_kb.md`执行系统服务。
