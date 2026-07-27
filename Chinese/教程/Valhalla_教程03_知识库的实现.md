# Valhalla 教程03

> 适合对象：完成了 Valhalla  教程01、02 的使用者，了解Valhalla的知识库系统的五层架构
>
> 学习目标：了解知识库的架构
>
> 预计时间：30-40 分钟

## 知识库和知识库系统的关系

注意分清两个概念：

- 知识库是一个特定领域的知识的集合。
- 知识库系统是一些知识库的集合，这样做的目的是让一些知识库可以共享知识库系统中的资源文件，以免每个知识库都建立自己独立的资源文件副本，造成浪费和管理困难。

## 知识库的架构

回顾知识库系统的五层架构：

| 五层架构 |
| --- |
| 图谱层 |
| 关系层 |
| 实体层/知识点层 |
| 资源层 |
| 文件层 |

各层逐层提供服务、逐层封装实现。

上层通过层间接口使用下层提供的能力，而下层不需要知道上层服务的具体实现。

知识库也依附于这五层结构，但是一个知识库系统中的所有知识库共享资源层和文件层，只构建自己的实体层、关系层、图谱层。

## 知识库的文件结构

`想快速了解Valhalla标准指令的一个诀窍是:查看codex的安装目录下.codex/skills/valhalla/router/router.md`

### 确定root

一个root就是一个知识库系统，表现为一个文件夹。

在Valhalla启动完成后，可以输入指令`状态`查看状态，其中包括目前使用的root。

也可以输入`root列表`或`所有root`或`列出所有root`查看当在登记在系统中的root。

第一次使用Valhalla时，使用指令`创建root <root路径> <root别名>`创建root。

如果想启动一个你的目标root，直接输入`切换root <root路径|root别名>`即可。

强烈建议在目标root启动之后再次输入`状态`查看状态。

### root的文件结构

在确定root后，使用指令`新建知识库 <知识库名>`新建知识库。

打开root文件夹，可以看到如下结构：

```text
    .valhalla/
        kb_status.md
    resource_registry.yaml
    resource_registry.md
    wiki_registry.yaml
    wiki_registry.md
    orphan_resources.md
    blacklist_registry.yaml
    Library/
        public_resources/
    Wiki/
```

`Library/`是该知识库系统的文件层，所有的原始资料文件必须放在这里。里面的`public_resources/`子文件夹是系统使用的资料备份，使用者不要操作该文件夹。

`resource_registry.yaml`是最主要的资源层构成，它把`Library/`中的资料登记为唯一的`resource_id`以供上层使用(`Library/`中的资料文件可能有很多份，
它们必须有一个统一标识，以免上层调用时出现混乱)。
`resource_registry.md`是`resource_registry.yaml`的人类可读映射，后面都采取这种约定，相同名称的文件中，yaml文件是机器易读文件，md是人类可读映射。

`blacklist_registry.yaml`是资源层的另一部分，是本root的全局屏蔽资源名单。

`Wiki/`文件夹是存放知识库的地方，知识库系统的上三层(entity,relationship,knowledge_graph)将在这里构建。

`Wiki/`中会有`Wiki_<知识库名>`这样的子文件夹，这些子文件夹就是这个知识库系统下的知识库。

### 知识库文件结构

打开`Wiki_<知识库名>`，会看到以下结构：

```text
Wiki/Wiki_<知识库名>/
    Wiki.md
    index.md
    log.md
    .virtualDatabase/
        machine/
            local_resources.yaml
            required_resources.yaml
            excluded_resources.yaml
        human/
            local_resources.md
            required_resources.md
            excluded_resources.md
    .registry/
        machine/
            entity_registry.yaml
            entity_resource_map.yaml
            relationship_registry.yaml
            knowledge_graph_registry.yaml
            conversation_entity_registry.yaml
            engineering_entity_registry.yaml
        human/
            entity_registry.md
            entity_resource_map.md
            relationship_registry.md
            knowledge_graph_registry.md
            conversation_entity_registry.md
            engineering_entity_registry.md
    entities/
    relationships/
        machine/
        human/
    knowledge_graph/
        machine/
        human/
    conversation_entities/
    engineering_entities/
```

其中`.registry/`存的的是相应层级的登记表，以便查阅。

#### 资源层

知识库使用虚拟资源层机制

`.virtualDatabase/`则是该知识库的一个虚拟资料层。

知识库是建立在该root的资源层之上的，但一个知识库是很有可能不用到root下所有的资料的，所以在这里使用三张资料表划定该知识库使用root下的哪些资源。

- `local_resources.yaml`本库资料表，记录该知识库的基本资料范围，这些资料在该知识库推进项目时可用可不用。
- `required_resources.yaml`必须资料表，记录该知识库推进项目时必须参考的资料。
- `excluded_resources.yaml`剔除资料表，记录该知识库推进项目时必须排除的资料。

虚拟资料库virtualDatabase=`local_resources∪required_resources-excluded_resources-blacklist`

可以通过指令手动修改这三张资料表。

#### 实体层

实体层分为三部分`entities/`,`conversation_entities/`,`engineering_entities/`，它们都用来存储知识点。

`entities/`是主要的entities的存储地，这些entities来自资源层的资源，是从资源中提取的知识点。`摄入`指令会提取

`conversation_entities/`是辅助的entities的存储地，这些entity来自使用者和Valhalla的对话，没有资源层作为支撑。

当使用者启动某个知识库与Valhalla进行查询、探讨之后，这些谈话内容也是一种知识，这些知识不应被丢弃，而是应该被存储起来，这就是`conversation_entities/`。

`engineering_entities/`，与`conversation_entities/`类似，将工程经验作为知识点存储起来，没有资源层作为支撑。

#### 关系层

`relationships/`用于存储entity之间的关系，比如`支撑`，`同等`，`矛盾`等等，你可以定制自己想要的在所有知识点中寻找的关系，
相关方法会在后面的开发教程中展示。

不要被`开发教程`吓到，得益于知识库系统的分层封装和知识库操作系统的偏向微内核的架构，Valhalla的开发流程简单得难以想象。
小小透露一点：在对Valhalla的开发中，你在绝大多数情况下甚至不需要自己亲自写文件。如果要写，得益于Valhalla由自然语言构建，也可以0门槛上手。

#### 图谱层

`knowledge_graph/`用于存储知识拓扑图，节点表示知识点，边表示关系。

该层是对关系层的一个拓展，可以存储某些特定关系的图，比如专门由矛盾关系构成的图，可以用于方案校验。

## 三探`摄入`操作

当了解了知识库的分层构建之后，我们再来看`摄入`的操作细节：

`文件层`操作：摄入操作的输入是一个文件名或者文件路径，Valhalla会先在当前root下的Library中确定该文件的存在。如果不存在，则报错返回

`资源层`操作：如果文件存在，则Valhalla下一步会验证该文件是否在资源层登记，拥有自己独一无二的`resource_id`，如果没登记，就进行登记以获得`resource_id`。

文件获得`resource_id`后，Valhalla会检查该资源是否在当前知识库的虚拟资料库中，如果不在，则将该resource_id添加到虚拟资料库中。

`实体层`操作：当该资料进入当前知识库的资料层后，Valhalla就开始基于该资源，在实体层通过提取其中的知识点构建知识实体。

一般而言，Valhalla的某个操作(根据微内核架构的惯例，也被称作系统服务)只会独立操作知识库系统中的一层，以达到脱耦效果，以免改动波及其他部分。

但为了方便，Valhalla还是将很多操作整合进了`摄入`中，否则如果每篇资料都要去手动经历`资源登记`，`进入虚拟资料库`，`摄入知识`这样的步骤，估计大多数人就放弃了。

这就是前面说过`摄入`操作是一个相当复杂的操作，当然不是最复杂的，目前最复杂的是`融合root`操作，它可以把不同的知识库系统融合为一个，实现多人的知识共享与协作。

当然，上述分步操作也是系统已有的，如果你想尝试，请参考router，自己分步尝试，这对理解Valhalla知识库系统的分层封装很有好处。

### 总结

本章节揭示了知识库建立的背后细节，展示了如何将前一章节讲述的`知识库系统`的`五层架构`这个抽象概念，通过Library，resource_registry，Wiki将概念实现。
