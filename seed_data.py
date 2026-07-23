"""
Seed data for the vocabulary system.
Generates 120+ words across CET-4/CET-6/IELTS word books,
with similar word groups and some learning records.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import random
from app import create_app
from models import db, Word, WordBook, WordBookItem, SimilarWordGroup, SimilarWordItem
from models import LearningRecord, WrongAnswer, DailyCheckin

app = create_app()

# ─── Sample Words ──────────────────────────────────────

WORDS = [
    # CET-4 Core (40 words)
    {"word": "abandon", "phonetic": "/əˈbændən/", "definition": "放弃；抛弃", "example_sentence": "They had to abandon the sinking ship.", "example_translation": "他们不得不放弃正在下沉的船。", "part_of_speech": "verb", "tags": "CET-4,高频"},
    {"word": "ability", "phonetic": "/əˈbɪləti/", "definition": "能力；才能", "example_sentence": "She has the ability to learn languages quickly.", "example_translation": "她有快速学习语言的能力。", "part_of_speech": "noun", "tags": "CET-4"},
    {"word": "absorb", "phonetic": "/əbˈzɔːrb/", "definition": "吸收；吸引", "example_sentence": "Plants absorb nutrients from the soil.", "example_translation": "植物从土壤中吸收养分。", "part_of_speech": "verb", "tags": "CET-4"},
    {"word": "abstract", "phonetic": "/ˈæbstrækt/", "definition": "抽象的；摘要", "example_sentence": "The concept is too abstract to understand easily.", "example_translation": "这个概念太抽象，不易理解。", "part_of_speech": "adjective", "tags": "CET-4"},
    {"word": "abundant", "phonetic": "/əˈbʌndənt/", "definition": "丰富的；充裕的", "example_sentence": "The region has abundant natural resources.", "example_translation": "这个地区有丰富的自然资源。", "part_of_speech": "adjective", "tags": "CET-4"},
    {"word": "academy", "phonetic": "/əˈkædəmi/", "definition": "学院；学会", "example_sentence": "He studied at the Royal Academy of Music.", "example_translation": "他在皇家音乐学院学习。", "part_of_speech": "noun", "tags": "CET-4"},
    {"word": "accelerate", "phonetic": "/əkˈseləreɪt/", "definition": "加速；促进", "example_sentence": "The car accelerated smoothly down the highway.", "example_translation": "汽车在高速公路上平稳加速。", "part_of_speech": "verb", "tags": "CET-4"},
    {"word": "access", "phonetic": "/ˈækses/", "definition": "通道；进入；访问", "example_sentence": "Students have access to the online library.", "example_translation": "学生可以访问在线图书馆。", "part_of_speech": "noun/verb", "tags": "CET-4,IT"},
    {"word": "accommodate", "phonetic": "/əˈkɒmədeɪt/", "definition": "容纳；适应；提供住宿", "example_sentence": "The hotel can accommodate up to 500 guests.", "example_translation": "这家酒店最多可容纳500位客人。", "part_of_speech": "verb", "tags": "CET-4,难拼写"},
    {"word": "accomplish", "phonetic": "/əˈkʌmplɪʃ/", "definition": "完成；实现", "example_sentence": "She accomplished her goal of running a marathon.", "example_translation": "她完成了跑马拉松的目标。", "part_of_speech": "verb", "tags": "CET-4"},
    {"word": "accurate", "phonetic": "/ˈækjərət/", "definition": "准确的；精确的", "example_sentence": "The weather forecast was surprisingly accurate.", "example_translation": "天气预报出奇地准确。", "part_of_speech": "adjective", "tags": "CET-4"},
    {"word": "achieve", "phonetic": "/əˈtʃiːv/", "definition": "达到；取得", "example_sentence": "Hard work helps you achieve your dreams.", "example_translation": "努力工作帮助你实现梦想。", "part_of_speech": "verb", "tags": "CET-4,高频"},
    {"word": "acknowledge", "phonetic": "/əkˈnɒlɪdʒ/", "definition": "承认；确认收到", "example_sentence": "He acknowledged his mistake publicly.", "example_translation": "他公开承认了自己的错误。", "part_of_speech": "verb", "tags": "CET-4"},
    {"word": "acquire", "phonetic": "/əˈkwaɪər/", "definition": "获得；习得", "example_sentence": "Children acquire language naturally.", "example_translation": "儿童自然地习得语言。", "part_of_speech": "verb", "tags": "CET-4"},
    {"word": "adapt", "phonetic": "/əˈdæpt/", "definition": "适应；改编", "example_sentence": "Animals adapt to their environment over time.", "example_translation": "动物随着时间的推移适应环境。", "part_of_speech": "verb", "tags": "CET-4"},
    {"word": "adequate", "phonetic": "/ˈædɪkwət/", "definition": "足够的；适当的", "example_sentence": "The facilities were adequate for our needs.", "example_translation": "设施对我们的需求来说是足够的。", "part_of_speech": "adjective", "tags": "CET-4"},
    {"word": "adjust", "phonetic": "/əˈdʒʌst/", "definition": "调整；适应", "example_sentence": "You need to adjust the settings for better performance.", "example_translation": "你需要调整设置以获得更好的性能。", "part_of_speech": "verb", "tags": "CET-4"},
    {"word": "administration", "phonetic": "/ədˌmɪnɪˈstreɪʃn/", "definition": "管理；行政", "example_sentence": "The administration announced new policies.", "example_translation": "行政管理部门宣布了新政策。", "part_of_speech": "noun", "tags": "CET-4"},
    {"word": "adolescent", "phonetic": "/ˌædəˈlesnt/", "definition": "青少年", "example_sentence": "Adolescents often face peer pressure.", "example_translation": "青少年经常面临同伴压力。", "part_of_speech": "noun", "tags": "CET-4"},
    {"word": "adopt", "phonetic": "/əˈdɒpt/", "definition": "采用；收养", "example_sentence": "The company decided to adopt a new strategy.", "example_translation": "公司决定采用新策略。", "part_of_speech": "verb", "tags": "CET-4"},
    {"word": "adverse", "phonetic": "/ˈædvɜːrs/", "definition": "不利的；相反的", "example_sentence": "The drug has some adverse side effects.", "example_translation": "这种药物有一些不良副作用。", "part_of_speech": "adjective", "tags": "CET-6"},
    {"word": "advocate", "phonetic": "/ˈædvəkeɪt/", "definition": "提倡；拥护者", "example_sentence": "She advocates for environmental protection.", "example_translation": "她倡导环境保护。", "part_of_speech": "verb/noun", "tags": "CET-6"},
    {"word": "aesthetic", "phonetic": "/iːsˈθetɪk/", "definition": "美学的；审美的", "example_sentence": "The building combines function with aesthetic appeal.", "example_translation": "这座建筑兼具功能性和美学吸引力。", "part_of_speech": "adjective", "tags": "CET-6"},
    {"word": "affection", "phonetic": "/əˈfekʃn/", "definition": "喜爱；感情", "example_sentence": "She showed great affection for her grandchildren.", "example_translation": "她对孙辈表现出深厚的感情。", "part_of_speech": "noun", "tags": "CET-6"},
    {"word": "aggressive", "phonetic": "/əˈɡresɪv/", "definition": "侵略的；好斗的；积极的", "example_sentence": "The company adopted an aggressive marketing campaign.", "example_translation": "公司采取了积极的营销策略。", "part_of_speech": "adjective", "tags": "CET-6"},
    {"word": "alliance", "phonetic": "/əˈlaɪəns/", "definition": "联盟；联合", "example_sentence": "The two countries formed a military alliance.", "example_translation": "两国建立了军事联盟。", "part_of_speech": "noun", "tags": "CET-6"},
    {"word": "allocate", "phonetic": "/ˈæləkeɪt/", "definition": "分配；拨出", "example_sentence": "Funds were allocated for education reform.", "example_translation": "资金被拨出用于教育改革。", "part_of_speech": "verb", "tags": "CET-6,商务"},
    {"word": "alternative", "phonetic": "/ɔːlˈtɜːrnətɪv/", "definition": "替代的；供替代的选择", "example_sentence": "We need to find alternative energy sources.", "example_translation": "我们需要寻找替代能源。", "part_of_speech": "adjective/noun", "tags": "CET-6,高频"},
    {"word": "ambiguous", "phonetic": "/æmˈbɪɡjuəs/", "definition": "模糊的；有歧义的", "example_sentence": "The contract language is ambiguous and open to interpretation.", "example_translation": "合同语言模糊不清，有多种解读。", "part_of_speech": "adjective", "tags": "CET-6"},
    {"word": "ambitious", "phonetic": "/æmˈbɪʃəs/", "definition": "有雄心的；野心勃勃的", "example_sentence": "She is an ambitious young entrepreneur.", "example_translation": "她是一位雄心勃勃的年轻企业家。", "part_of_speech": "adjective", "tags": "CET-6"},
    {"word": "anonymous", "phonetic": "/əˈnɒnɪməs/", "definition": "匿名的", "example_sentence": "The donation was made by an anonymous benefactor.", "example_translation": "这笔捐款是一位匿名捐助者提供的。", "part_of_speech": "adjective", "tags": "CET-6"},
    {"word": "anticipate", "phonetic": "/ænˈtɪsɪpeɪt/", "definition": "预期；期望", "example_sentence": "We anticipate a large crowd at the concert.", "example_translation": "我们预计音乐会会有大量观众。", "part_of_speech": "verb", "tags": "CET-6"},
    {"word": "appreciate", "phonetic": "/əˈpriːʃieɪt/", "definition": "感激；欣赏；升值", "example_sentence": "I really appreciate your help with this project.", "example_translation": "我真的很感激你对这个项目的帮助。", "part_of_speech": "verb", "tags": "CET-4,高频"},
    {"word": "approach", "phonetic": "/əˈprəʊtʃ/", "definition": "方法；接近", "example_sentence": "We need a different approach to solve this problem.", "example_translation": "我们需要不同的方法来解决此问题。", "part_of_speech": "noun/verb", "tags": "CET-4,高频"},
    {"word": "appropriate", "phonetic": "/əˈprəʊpriət/", "definition": "适当的；合适的", "example_sentence": "Please dress in appropriate attire for the interview.", "example_translation": "面试请穿着得体。", "part_of_speech": "adjective", "tags": "CET-4"},
    {"word": "approximate", "phonetic": "/əˈprɒksɪmət/", "definition": "大约的；近似的", "example_sentence": "The approximate cost of the project is $10,000.", "example_translation": "项目的大约成本是1万美元。", "part_of_speech": "adjective", "tags": "CET-4"},
    {"word": "artificial", "phonetic": "/ˌɑːrtɪˈfɪʃl/", "definition": "人工的；人造的", "example_sentence": "Artificial intelligence is transforming many industries.", "example_translation": "人工智能正在转变许多行业。", "part_of_speech": "adjective", "tags": "CET-4,科技"},
    {"word": "asset", "phonetic": "/ˈæset/", "definition": "资产；优点", "example_sentence": "Her language skills are a valuable asset to the company.", "example_translation": "她的语言技能是公司的宝贵资产。", "part_of_speech": "noun", "tags": "CET-4,商务"},
    {"word": "associate", "phonetic": "/əˈsəʊʃieɪt/", "definition": "联系；关联；伙伴", "example_sentence": "People often associate success with wealth.", "example_translation": "人们经常将成功与财富联系起来。", "part_of_speech": "verb/noun", "tags": "CET-4"},
    {"word": "assume", "phonetic": "/əˈsjuːm/", "definition": "假设；承担", "example_sentence": "Don't assume that everything will go as planned.", "example_translation": "不要假设一切都会按计划进行。", "part_of_speech": "verb", "tags": "CET-4"},

    # More words (CET-6 & advanced)
    {"word": "barrier", "phonetic": "/ˈbæriər/", "definition": "障碍；屏障", "example_sentence": "Language barriers can make communication difficult.", "example_translation": "语言障碍会使沟通困难。", "part_of_speech": "noun", "tags": "CET-4"},
    {"word": "beneficial", "phonetic": "/ˌbenɪˈfɪʃl/", "definition": "有益的；有利的", "example_sentence": "Regular exercise is beneficial to your health.", "example_translation": "定期锻炼对你的健康有益。", "part_of_speech": "adjective", "tags": "CET-4"},
    {"word": "bureaucracy", "phonetic": "/bjʊəˈrɒkrəsi/", "definition": "官僚机构；官僚主义", "example_sentence": "The bureaucracy slowed down the approval process.", "example_translation": "官僚机构延缓了审批流程。", "part_of_speech": "noun", "tags": "CET-6"},
    {"word": "candidate", "phonetic": "/ˈkændɪdət/", "definition": "候选人；应试者", "example_sentence": "There are three strong candidates for the position.", "example_translation": "这个职位有三个强有力的候选人。", "part_of_speech": "noun", "tags": "CET-4"},
    {"word": "capability", "phonetic": "/ˌkeɪpəˈbɪləti/", "definition": "能力；才能", "example_sentence": "The new system has enhanced processing capabilities.", "example_translation": "新系统具有增强的处理能力。", "part_of_speech": "noun", "tags": "CET-6"},
    {"word": "celebrity", "phonetic": "/səˈlebrəti/", "definition": "名人；名声", "example_sentence": "The celebrity was surrounded by fans.", "example_translation": "这位名人被粉丝们围住了。", "part_of_speech": "noun", "tags": "CET-6"},
    {"word": "circumstance", "phonetic": "/ˈsɜːrkəmstæns/", "definition": "环境；情况", "example_sentence": "Under normal circumstances, the flight takes two hours.", "example_translation": "在正常情况下，飞行需要两小时。", "part_of_speech": "noun", "tags": "CET-4"},
    {"word": "collapse", "phonetic": "/kəˈlæps/", "definition": "崩溃；倒塌", "example_sentence": "The building collapsed during the earthquake.", "example_translation": "建筑在地震中倒塌了。", "part_of_speech": "verb", "tags": "CET-4"},
    {"word": "commodity", "phonetic": "/kəˈmɒdəti/", "definition": "商品；日用品", "example_sentence": "Oil is one of the world's most traded commodities.", "example_translation": "石油是世界上交易量最大的商品之一。", "part_of_speech": "noun", "tags": "CET-6,商务"},
    {"word": "compensate", "phonetic": "/ˈkɒmpenseɪt/", "definition": "补偿；赔偿", "example_sentence": "The company will compensate you for the damage.", "example_translation": "公司会为损坏赔偿你。", "part_of_speech": "verb", "tags": "CET-6"},
    {"word": "compliment", "phonetic": "/ˈkɒmplɪment/", "definition": "赞美；恭维", "example_sentence": "She received many compliments on her presentation.", "example_translation": "她的演讲得到了许多赞美。", "part_of_speech": "noun/verb", "tags": "CET-6,易混淆"},
    {"word": "compromise", "phonetic": "/ˈkɒmprəmaɪz/", "definition": "妥协；折中", "example_sentence": "Both sides reached a compromise after long negotiations.", "example_translation": "双方经过长时间谈判达成了妥协。", "part_of_speech": "noun/verb", "tags": "CET-6"},
    {"word": "concentrate", "phonetic": "/ˈkɒnsntreɪt/", "definition": "集中；专注", "example_sentence": "I need silence to concentrate on my work.", "example_translation": "我需要安静来集中精力工作。", "part_of_speech": "verb", "tags": "CET-4"},
    {"word": "conduct", "phonetic": "/kənˈdʌkt/", "definition": "进行；实施；行为", "example_sentence": "The university will conduct research on climate change.", "example_translation": "该大学将进行气候变化研究。", "part_of_speech": "verb/noun", "tags": "CET-4"},
    {"word": "consequence", "phonetic": "/ˈkɒnsɪkwəns/", "definition": "结果；后果", "example_sentence": "Every action has its consequences.", "example_translation": "每个行为都有其后果。", "part_of_speech": "noun", "tags": "CET-4"},
    {"word": "conservative", "phonetic": "/kənˈsɜːrvətɪv/", "definition": "保守的", "example_sentence": "He comes from a conservative family background.", "example_translation": "他来自一个保守的家庭背景。", "part_of_speech": "adjective", "tags": "CET-6"},
    {"word": "consistent", "phonetic": "/kənˈsɪstənt/", "definition": "一致的；始终如一的", "example_sentence": "Her performance has been consistently excellent.", "example_translation": "她的表现一直很出色。", "part_of_speech": "adjective", "tags": "CET-4"},
    {"word": "contemporary", "phonetic": "/kənˈtemprəri/", "definition": "当代的；同时代的", "example_sentence": "The gallery exhibits contemporary art.", "example_translation": "画廊展出当代艺术。", "part_of_speech": "adjective", "tags": "CET-6"},
    {"word": "contradict", "phonetic": "/ˌkɒntrəˈdɪkt/", "definition": "矛盾；反驳", "example_sentence": "His actions contradict his words.", "example_translation": "他的行为与他的言语相矛盾。", "part_of_speech": "verb", "tags": "CET-6"},
    {"word": "controversy", "phonetic": "/ˈkɒntrəvɜːrsi/", "definition": "争议；争论", "example_sentence": "The new policy sparked a heated controversy.", "example_translation": "新政策引发了激烈的争议。", "part_of_speech": "noun", "tags": "CET-6"},
    {"word": "conventional", "phonetic": "/kənˈvenʃənl/", "definition": "传统的；常规的", "example_sentence": "Conventional wisdom is not always correct.", "example_translation": "传统智慧并不总是正确的。", "part_of_speech": "adjective", "tags": "CET-6"},
    {"word": "cooperate", "phonetic": "/kəʊˈɒpəreɪt/", "definition": "合作；协作", "example_sentence": "The two departments cooperate closely on projects.", "example_translation": "两个部门在项目上密切合作。", "part_of_speech": "verb", "tags": "CET-4"},
    {"word": "correspond", "phonetic": "/ˌkɒrəˈspɒnd/", "definition": "对应；通信", "example_sentence": "The numbers correspond to the items on the list.", "example_translation": "数字对应列表上的项目。", "part_of_speech": "verb", "tags": "CET-6"},
    {"word": "crucial", "phonetic": "/ˈkruːʃl/", "definition": "关键的；至关重要的", "example_sentence": "This decision is crucial for the company's future.", "example_translation": "这个决定对公司的未来至关重要。", "part_of_speech": "adjective", "tags": "CET-6,高频"},
    {"word": "curriculum", "phonetic": "/kəˈrɪkjələm/", "definition": "课程", "example_sentence": "The school has updated its science curriculum.", "example_translation": "学校更新了科学课程。", "part_of_speech": "noun", "tags": "CET-6"},
    {"word": "deceive", "phonetic": "/dɪˈsiːv/", "definition": "欺骗；蒙蔽", "example_sentence": "Don't be deceived by appearances.", "example_translation": "不要被外表所欺骗。", "part_of_speech": "verb", "tags": "CET-4"},
    {"word": "defect", "phonetic": "/ˈdiːfekt/", "definition": "缺陷；缺点", "example_sentence": "The product was recalled due to a manufacturing defect.", "example_translation": "产品因制造缺陷被召回。", "part_of_speech": "noun", "tags": "CET-6"},
    {"word": "deliberate", "phonetic": "/dɪˈlɪbərət/", "definition": "故意的；深思熟虑的", "example_sentence": "It was a deliberate attempt to mislead the public.", "example_translation": "这是故意误导公众的企图。", "part_of_speech": "adjective", "tags": "CET-6"},
    {"word": "demonstrate", "phonetic": "/ˈdemənstreɪt/", "definition": "展示；证明；示威", "example_sentence": "The experiment demonstrates the principle of gravity.", "example_translation": "这个实验展示了引力原理。", "part_of_speech": "verb", "tags": "CET-4"},
    {"word": "depression", "phonetic": "/dɪˈpreʃn/", "definition": "抑郁；萧条", "example_sentence": "The economic depression affected millions of people.", "example_translation": "经济萧条影响了数百万人。", "part_of_speech": "noun", "tags": "CET-4"},
    {"word": "derive", "phonetic": "/dɪˈraɪv/", "definition": "源于；获得", "example_sentence": "Many English words derive from Latin.", "example_translation": "许多英语单词源于拉丁语。", "part_of_speech": "verb", "tags": "CET-6"},
    {"word": "dilemma", "phonetic": "/dɪˈlemə/", "definition": "困境；两难", "example_sentence": "She faced the dilemma of choosing between career and family.", "example_translation": "她面临着事业与家庭之间的两难选择。", "part_of_speech": "noun", "tags": "CET-6"},
    {"word": "diminish", "phonetic": "/dɪˈmɪnɪʃ/", "definition": "减少；缩小", "example_sentence": "The pain will gradually diminish over time.", "example_translation": "疼痛会随着时间逐渐减轻。", "part_of_speech": "verb", "tags": "CET-6"},
    {"word": "discriminate", "phonetic": "/dɪˈskrɪmɪneɪt/", "definition": "歧视；区分", "example_sentence": "It is illegal to discriminate based on race or gender.", "example_translation": "基于种族或性别的歧视是非法的。", "part_of_speech": "verb", "tags": "CET-6"},
    {"word": "distinct", "phonetic": "/dɪˈstɪŋkt/", "definition": "明显的；不同的", "example_sentence": "There is a distinct difference between the two concepts.", "example_translation": "这两个概念之间有明显的区别。", "part_of_speech": "adjective", "tags": "CET-4"},
    {"word": "distribute", "phonetic": "/dɪˈstrɪbjuːt/", "definition": "分配；分发", "example_sentence": "Food and water were distributed to the victims.", "example_translation": "食物和水被分发给灾民。", "part_of_speech": "verb", "tags": "CET-4"},

    # Advanced / IELTS (30 words)
    {"word": "eloquent", "phonetic": "/ˈeləkwənt/", "definition": "雄辩的；有口才的", "example_sentence": "She gave an eloquent speech at the ceremony.", "example_translation": "她在典礼上发表了雄辩的演讲。", "part_of_speech": "adjective", "tags": "IELTS"},
    {"word": "embrace", "phonetic": "/ɪmˈbreɪs/", "definition": "拥抱；欣然接受", "example_sentence": "We should embrace change rather than fear it.", "example_translation": "我们应该拥抱变化而非恐惧它。", "part_of_speech": "verb", "tags": "IELTS"},
    {"word": "endeavor", "phonetic": "/ɪnˈdevər/", "definition": "努力；尽力", "example_sentence": "The team will endeavor to complete the project on time.", "example_translation": "团队将努力按时完成项目。", "part_of_speech": "noun/verb", "tags": "IELTS"},
    {"word": "enhance", "phonetic": "/ɪnˈhɑːns/", "definition": "增强；提高", "example_sentence": "Technology can enhance the learning experience.", "example_translation": "技术可以增强学习体验。", "part_of_speech": "verb", "tags": "IELTS,高频"},
    {"word": "enormous", "phonetic": "/ɪˈnɔːrməs/", "definition": "巨大的；庞大的", "example_sentence": "The project required an enormous amount of resources.", "example_translation": "这个项目需要大量资源。", "part_of_speech": "adjective", "tags": "CET-4"},
    {"word": "entrepreneur", "phonetic": "/ˌɒntrəprəˈnɜːr/", "definition": "企业家", "example_sentence": "The young entrepreneur founded three successful startups.", "example_translation": "这位年轻企业家创立了三家成功的创业公司。", "part_of_speech": "noun", "tags": "IELTS,商务"},
    {"word": "environment", "phonetic": "/ɪnˈvaɪrənmənt/", "definition": "环境", "example_sentence": "We must protect the environment for future generations.", "example_translation": "我们必须为后代保护环境。", "part_of_speech": "noun", "tags": "CET-4,高频"},
    {"word": "ephemeral", "phonetic": "/ɪˈfemərəl/", "definition": "短暂的；转瞬即逝的", "example_sentence": "The beauty of cherry blossoms is ephemeral.", "example_translation": "樱花之美是转瞬即逝的。", "part_of_speech": "adjective", "tags": "IELTS,高级"},
    {"word": "equivalent", "phonetic": "/ɪˈkwɪvələnt/", "definition": "相等的；等价的", "example_sentence": "One mile is equivalent to approximately 1.6 kilometers.", "example_translation": "一英里大约等于1.6公里。", "part_of_speech": "adjective", "tags": "CET-4"},
    {"word": "essential", "phonetic": "/ɪˈsenʃl/", "definition": "必要的；本质的", "example_sentence": "Water is essential for all forms of life.", "example_translation": "水对所有生命形式都是必要的。", "part_of_speech": "adjective", "tags": "CET-4,高频"},
    {"word": "evaluate", "phonetic": "/ɪˈvæljueɪt/", "definition": "评估；评价", "example_sentence": "Teachers evaluate students based on their performance.", "example_translation": "教师根据表现评估学生。", "part_of_speech": "verb", "tags": "CET-4"},
    {"word": "evident", "phonetic": "/ˈevɪdənt/", "definition": "明显的；显然的", "example_sentence": "It is evident that climate change is accelerating.", "example_translation": "很明显气候变化正在加速。", "part_of_speech": "adjective", "tags": "CET-6"},
    {"word": "exaggerate", "phonetic": "/ɪɡˈzædʒəreɪt/", "definition": "夸张；夸大", "example_sentence": "Don't exaggerate the difficulties; it's not that hard.", "example_translation": "不要夸大困难；没有那么难。", "part_of_speech": "verb", "tags": "CET-6"},
    {"word": "execute", "phonetic": "/ˈeksɪkjuːt/", "definition": "执行；实施", "example_sentence": "The plan was executed with precision.", "example_translation": "计划被精确执行。", "part_of_speech": "verb", "tags": "CET-6"},
    {"word": "explicit", "phonetic": "/ɪkˈsplɪsɪt/", "definition": "明确的；清楚的", "example_sentence": "The instructions were very explicit and easy to follow.", "example_translation": "说明非常明确，易于遵循。", "part_of_speech": "adjective", "tags": "CET-6"},
    {"word": "exploit", "phonetic": "/ɪkˈsplɔɪt/", "definition": "利用；剥削；开发", "example_sentence": "The company was accused of exploiting its workers.", "example_translation": "该公司被指控剥削工人。", "part_of_speech": "verb", "tags": "CET-6"},
    {"word": "flexible", "phonetic": "/ˈfleksəbl/", "definition": "灵活的；柔韧的", "example_sentence": "A flexible schedule allows for better work-life balance.", "example_translation": "灵活的时间表可以实现更好的工作生活平衡。", "part_of_speech": "adjective", "tags": "CET-4"},
    {"word": "fluctuate", "phonetic": "/ˈflʌktʃueɪt/", "definition": "波动；起伏", "example_sentence": "Stock prices fluctuate throughout the day.", "example_translation": "股票价格在全天波动。", "part_of_speech": "verb", "tags": "CET-6"},
    {"word": "fundamental", "phonetic": "/ˌfʌndəˈmentl/", "definition": "基本的；根本的", "example_sentence": "Freedom of speech is a fundamental human right.", "example_translation": "言论自由是一项基本人权。", "part_of_speech": "adjective", "tags": "CET-6,高频"},
    {"word": "generate", "phonetic": "/ˈdʒenəreɪt/", "definition": "产生；生成", "example_sentence": "The solar panels generate enough electricity for the building.", "example_translation": "太阳能板为大楼产生足够的电力。", "part_of_speech": "verb", "tags": "CET-4"},
    {"word": "genuine", "phonetic": "/ˈdʒenjuɪn/", "definition": "真正的；真诚的", "example_sentence": "She showed genuine concern for her friend's wellbeing.", "example_translation": "她对朋友的幸福表现出真诚的关心。", "part_of_speech": "adjective", "tags": "CET-6"},
    {"word": "guarantee", "phonetic": "/ˌɡærənˈtiː/", "definition": "保证；担保", "example_sentence": "The product comes with a 5-year guarantee.", "example_translation": "该产品附带5年保修。", "part_of_speech": "noun/verb", "tags": "CET-4"},
    {"word": "hierarchy", "phonetic": "/ˈhaɪərɑːrki/", "definition": "等级制度；层次结构", "example_sentence": "The company has a flat organizational hierarchy.", "example_translation": "公司有扁平化的组织架构。", "part_of_speech": "noun", "tags": "IELTS"},
    {"word": "hypothesize", "phonetic": "/haɪˈpɒθəsaɪz/", "definition": "假设；推测", "example_sentence": "Scientists hypothesize that the planet may contain water.", "example_translation": "科学家推测这颗行星可能含有水。", "part_of_speech": "verb", "tags": "IELTS,学术"},
    {"word": "identical", "phonetic": "/aɪˈdentɪkl/", "definition": "完全相同的；一样的", "example_sentence": "The two samples are nearly identical in composition.", "example_translation": "这两个样本在成分上几乎相同。", "part_of_speech": "adjective", "tags": "CET-4"},
    {"word": "illuminate", "phonetic": "/ɪˈluːmɪneɪt/", "definition": "照亮；阐明", "example_sentence": "The research illuminates an important aspect of human behavior.", "example_translation": "这项研究阐明了人类行为的一个重要方面。", "part_of_speech": "verb", "tags": "IELTS"},
    {"word": "implement", "phonetic": "/ˈɪmplɪment/", "definition": "实施；执行", "example_sentence": "The government will implement the new policy next month.", "example_translation": "政府将于下月实施新政策。", "part_of_speech": "verb", "tags": "CET-6,商务"},
    {"word": "implicit", "phonetic": "/ɪmˈplɪsɪt/", "definition": "含蓄的；隐含的", "example_sentence": "There was an implicit understanding between them.", "example_translation": "他们之间有一种含蓄的理解。", "part_of_speech": "adjective", "tags": "CET-6"},
    {"word": "inevitable", "phonetic": "/ɪnˈevɪtəbl/", "definition": "不可避免的", "example_sentence": "Change is an inevitable part of life.", "example_translation": "变化是生活中不可避免的一部分。", "part_of_speech": "adjective", "tags": "CET-6"},
    {"word": "infrastructure", "phonetic": "/ˈɪnfrəstrʌktʃər/", "definition": "基础设施", "example_sentence": "The city is investing heavily in infrastructure development.", "example_translation": "该市正在大力投资基础设施建设。", "part_of_speech": "noun", "tags": "IELTS,商务"},
    {"word": "inherent", "phonetic": "/ɪnˈherənt/", "definition": "固有的；内在的", "example_sentence": "There are risks inherent in any investment.", "example_translation": "任何投资都有固有风险。", "part_of_speech": "adjective", "tags": "IELTS"},
    {"word": "innovation", "phonetic": "/ˌɪnəˈveɪʃn/", "definition": "创新；革新", "example_sentence": "Technological innovation drives economic growth.", "example_translation": "技术创新推动经济增长。", "part_of_speech": "noun", "tags": "CET-6,科技"},
    {"word": "integrate", "phonetic": "/ˈɪntɪɡreɪt/", "definition": "整合；融合", "example_sentence": "The school aims to integrate technology into every classroom.", "example_translation": "学校旨在将技术整合到每个教室中。", "part_of_speech": "verb", "tags": "CET-6"},
    {"word": "intervene", "phonetic": "/ˌɪntərˈviːn/", "definition": "干预；介入", "example_sentence": "The government had to intervene to stabilize the market.", "example_translation": "政府不得不干预以稳定市场。", "part_of_speech": "verb", "tags": "IELTS"},
    {"word": "intricate", "phonetic": "/ˈɪntrɪkət/", "definition": "复杂的；错综的", "example_sentence": "The watch mechanism is incredibly intricate.", "example_translation": "手表机芯非常复杂精细。", "part_of_speech": "adjective", "tags": "IELTS,高级"},
    {"word": "legitimate", "phonetic": "/lɪˈdʒɪtɪmət/", "definition": "合法的；正当的", "example_sentence": "The company has a legitimate reason for the price increase.", "example_translation": "公司有正当理由提高价格。", "part_of_speech": "adjective", "tags": "IELTS"},
    {"word": "manipulate", "phonetic": "/məˈnɪpjuleɪt/", "definition": "操纵；操作", "example_sentence": "He tried to manipulate the data to support his theory.", "example_translation": "他试图操纵数据来支持他的理论。", "part_of_speech": "verb", "tags": "IELTS"},
    {"word": "mechanism", "phonetic": "/ˈmekənɪzəm/", "definition": "机制；原理", "example_sentence": "The body has natural defense mechanisms against disease.", "example_translation": "身体有天然的防御机制来对抗疾病。", "part_of_speech": "noun", "tags": "IELTS,学术"},
    {"word": "meticulous", "phonetic": "/məˈtɪkjələs/", "definition": "一丝不苟的；细致的", "example_sentence": "She is meticulous in her research methodology.", "example_translation": "她在研究方法上一丝不苟。", "part_of_speech": "adjective", "tags": "IELTS,高级"},
    {"word": "negotiate", "phonetic": "/nɪˈɡəʊʃieɪt/", "definition": "谈判；协商", "example_sentence": "The union will negotiate better working conditions.", "example_translation": "工会将谈判争取更好的工作条件。", "part_of_speech": "verb", "tags": "CET-4,商务"},
    {"word": "notion", "phonetic": "/ˈnəʊʃn/", "definition": "概念；观念", "example_sentence": "The notion of time varies across cultures.", "example_translation": "时间的概念因文化而异。", "part_of_speech": "noun", "tags": "CET-6"},
    {"word": "nuisance", "phonetic": "/ˈnjuːsns/", "definition": "讨厌的人或事；麻烦", "example_sentence": "The construction noise was a constant nuisance.", "example_translation": "施工噪音是一个持续的麻烦。", "part_of_speech": "noun", "tags": "CET-6"},
    {"word": "obstacle", "phonetic": "/ˈɒbstəkl/", "definition": "障碍；妨碍", "example_sentence": "Lack of funding is the main obstacle to the project.", "example_translation": "缺乏资金是项目的主要障碍。", "part_of_speech": "noun", "tags": "CET-6"},
    {"word": "paradigm", "phonetic": "/ˈpærədaɪm/", "definition": "范式；典范", "example_sentence": "The discovery led to a paradigm shift in physics.", "example_translation": "这一发现导致了物理学的范式转变。", "part_of_speech": "noun", "tags": "IELTS,学术"},
    {"word": "phenomenon", "phonetic": "/fɪˈnɒmɪnən/", "definition": "现象", "example_sentence": "Global warming is a complex phenomenon.", "example_translation": "全球变暖是一个复杂的现象。", "part_of_speech": "noun", "tags": "CET-6,学术"},
    {"word": "plausible", "phonetic": "/ˈplɔːzəbl/", "definition": "似乎合理的；似乎可信的", "example_sentence": "His explanation sounds plausible but I'm not convinced.", "example_translation": "他的解释听起来合理，但我不完全信服。", "part_of_speech": "adjective", "tags": "IELTS"},
    {"word": "predominant", "phonetic": "/prɪˈdɒmɪnənt/", "definition": "主要的；主导的", "example_sentence": "English is the predominant language of international business.", "example_translation": "英语是国际商务的主导语言。", "part_of_speech": "adjective", "tags": "IELTS"},
    {"word": "preliminary", "phonetic": "/prɪˈlɪmɪnəri/", "definition": "初步的；预备的", "example_sentence": "The preliminary results are very encouraging.", "example_translation": "初步结果非常令人鼓舞。", "part_of_speech": "adjective", "tags": "IELTS"},
    {"word": "profound", "phonetic": "/prəˈfaʊnd/", "definition": "深刻的；深远的", "example_sentence": "The experience had a profound impact on her life.", "example_translation": "这次经历对她的生活产生了深远影响。", "part_of_speech": "adjective", "tags": "IELTS,高频"},
    {"word": "prominent", "phonetic": "/ˈprɒmɪnənt/", "definition": "突出的；著名的", "example_sentence": "She is a prominent figure in the field of neuroscience.", "example_translation": "她是神经科学领域的著名人物。", "part_of_speech": "adjective", "tags": "IELTS"},
    {"word": "prosperous", "phonetic": "/ˈprɒspərəs/", "definition": "繁荣的；兴旺的", "example_sentence": "The country has become increasingly prosperous.", "example_translation": "这个国家变得越来越繁荣。", "part_of_speech": "adjective", "tags": "IELTS"},
    {"word": "reconcile", "phonetic": "/ˈrekənsaɪl/", "definition": "调和；和解", "example_sentence": "It's difficult to reconcile work and family responsibilities.", "example_translation": "很难调和工作和家庭责任。", "part_of_speech": "verb", "tags": "IELTS"},
    {"word": "sophisticated", "phonetic": "/səˈfɪstɪkeɪtɪd/", "definition": "复杂精密的；老练的", "example_sentence": "The software uses sophisticated algorithms.", "example_translation": "该软件使用复杂的算法。", "part_of_speech": "adjective", "tags": "IELTS,科技"},
    {"word": "ubiquitous", "phonetic": "/juːˈbɪkwɪtəs/", "definition": "无处不在的", "example_sentence": "Smartphones have become ubiquitous in modern society.", "example_translation": "智能手机在现代社会已无处不在。", "part_of_speech": "adjective", "tags": "IELTS,高级"},
    {"word": "undermine", "phonetic": "/ˌʌndərˈmaɪn/", "definition": "逐渐削弱；破坏", "example_sentence": "Constant criticism can undermine a person's confidence.", "example_translation": "持续的批评会削弱一个人的信心。", "part_of_speech": "verb", "tags": "IELTS"},
    {"word": "versatile", "phonetic": "/ˈvɜːrsətaɪl/", "definition": "多才多艺的；多功能的", "example_sentence": "She is a versatile musician who plays five instruments.", "example_translation": "她是一位多才多艺的音乐家，会演奏五种乐器。", "part_of_speech": "adjective", "tags": "IELTS"},
    {"word": "vulnerable", "phonetic": "/ˈvʌlnərəbl/", "definition": "脆弱的；易受伤的", "example_sentence": "Children are particularly vulnerable to online dangers.", "example_translation": "儿童特别容易受到网络危险的伤害。", "part_of_speech": "adjective", "tags": "IELTS"},
]


def seed():
    with app.app_context():
        # Clear existing data
        db.drop_all()
        db.create_all()

        # ─── Create Words ───
        word_objects = []
        for w in WORDS:
            obj = Word(
                word=w["word"],
                phonetic=w["phonetic"],
                definition=w["definition"],
                example_sentence=w["example_sentence"],
                example_translation=w["example_translation"],
                part_of_speech=w["part_of_speech"],
                tags=w["tags"],
            )
            db.session.add(obj)
            word_objects.append(obj)

        db.session.flush()
        print(f"✅ Created {len(word_objects)} words")

        # ─── Create Word Books ───
        books_data = [
            {"name": "CET-4 核心词汇", "description": "大学英语四级考试高频核心词汇", "cover_color": "#4A90D9"},
            {"name": "CET-6 进阶词汇", "description": "大学英语六级考试进阶词汇", "cover_color": "#E74C3C"},
            {"name": "雅思必备词汇", "description": "IELTS 考试常见学术词汇", "cover_color": "#2ECC71"},
            {"name": "商务英语", "description": "商务场景常用词汇和表达", "cover_color": "#F39C12"},
        ]

        books = []
        for bd in books_data:
            book = WordBook(**bd)
            db.session.add(book)
            books.append(book)

        db.session.flush()
        print(f"✅ Created {len(books)} word books")

        # ─── Assign words to books ───
        book_assignments = {
            "CET-4 核心词汇": {"tags": ["CET-4"], "count": 40},
            "CET-6 进阶词汇": {"tags": ["CET-6"], "count": 50},
            "雅思必备词汇": {"tags": ["IELTS"], "count": 50},
            "商务英语": {"tags": ["商务"], "count": 20},
        }

        for book in books:
            tags = book_assignments[book.name]["tags"]
            matching_words = [
                w for w in word_objects
                if any(tag in w.tags for tag in tags)
            ]

            # If insufficient by tag, fill with random words
            if len(matching_words) < 10:
                import random
                random.shuffle(word_objects)
                extra = [w for w in word_objects if w not in matching_words]
                matching_words += extra[:20-len(matching_words)]

            for w in matching_words:
                db.session.add(WordBookItem(wordbook_id=book.id, word_id=w.id))

        db.session.flush()
        print(f"✅ Assigned words to books")

        # ─── Create Similar Word Groups ───
        similar_groups_data = [
            {
                "name": "abandon / abundant / abundant",
                "description": "都以 a 开头，拼写和发音相近，注意区分",
                "words": ["abandon", "abundant", "absorb"],
            },
            {
                "name": "adapt / adopt / adept",
                "description": "三个词形近但含义完全不同：适应/采用/熟练的",
                "words": ["adapt", "adopt"],
            },
            {
                "name": "affect / effect / defect",
                "description": "容易混淆的词根 -fect 系列",
                "words": ["defect", "effect"],
            },
            {
                "name": "compliment / complement / implement",
                "description": "-ment 结尾的易混淆词",
                "words": ["compliment", "implement", "compensate"],
            },
            {
                "name": "explicit / implicit",
                "description": "反义词对：明确的 vs 含蓄的",
                "words": ["explicit", "implicit"],
            },
            {
                "name": "acquire / inquire / require",
                "description": "-quire 词根系列",
                "words": ["acquire"],
            },
            {
                "name": "concentrate / contemplate / contemporary",
                "description": "con- 开头长单词，拼写易混淆",
                "words": ["concentrate", "contemporary", "contradict"],
            },
        ]

        # Build word lookup
        word_map = {w.word: w for w in word_objects}

        for sg_data in similar_groups_data:
            group = SimilarWordGroup(name=sg_data["name"], description=sg_data["description"])
            db.session.add(group)
            db.session.flush()

            for word_text in sg_data["words"]:
                if word_text in word_map:
                    db.session.add(SimilarWordItem(group_id=group.id, word_id=word_map[word_text].id))

        print(f"✅ Created {len(similar_groups_data)} similar word groups")

        # ─── Commit (no fake activity data) ───
        db.session.commit()
        print("\n🎉 种子数据创建完毕！")
        print(f"   📝 {len(word_objects)} 个单词")
        print(f"   📚 {len(books)} 本单词书")
        print(f"   🔗 {len(similar_groups_data)} 个形近词组")
        print(f"   🆕 学习记录、错题本、打卡记录均为空白，从现在开始积累")
        print("\n运行: ./venv/bin/python app.py")
        print("访问: http://localhost:5000")


if __name__ == "__main__":
    seed()
