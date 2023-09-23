from pydantic import BaseModel, Field
from typing import Optional, Union, Literal, Any, Type, ClassVar
from models.base import ModelBase


class CoreSchema(BaseModel):
    id: Optional[int] = None

    def dict(
        self,
        *,
        include: Any = None,
        exclude: Any = None,
        by_alias: bool = False,
        exclude_unset: bool = False,
        exclude_defaults: bool = False,
        exclude_none: bool = False,
    ) -> Any:
        """
        - include: Union[SetIntStr, DictIntStrAny] (기본값: None)
            반환할 속성의 집합이나 딕셔너리를 지정합니다. 지정된 속성만 딕셔너리에 포함됩니다.
            예: include={"name", "age"}는 name과 age 속성만 반환합니다.

        - exclude: Union[SetIntStr, DictIntStrAny] (기본값: None)
            반환에서 제외할 속성의 집합이나 딕셔너리를 지정합니다.
            예: exclude={"name", "age"}는 name과 age를 제외한 모든 속성을 반환합니다.

        - by_alias: bool (기본값: False)
            True로 설정하면, 모델의 속성 이름 대신 alias를 사용하여 딕셔너리 키를 생성합니다. (모델 필드 정의에서 alias 설정이 있는 경우)


        - exclude_unset: bool (기본값: False)
            True로 설정하면, 설정되지 않은 모든 값(즉, 값이 제공되지 않아서 기본값을 사용하는 값)은 반환된 딕셔너리에서 제외됩니다.

        - exclude_defaults: bool (기본값: False)
            True로 설정하면, 모델에서 기본값으로 설정된 모든 값은 딕셔너리에서 제외됩니다.

        - exclude_none: bool (기본값: False)
            True로 설정하면, None 값이 있는 속성은 딕셔너리에서 제외됩니다.
            이러한 매개변수들은 Pydantic 모델에서 딕셔너리로의 변환을 매우 유연하게 제어하도록 도와줍니다. 원하는 대로 데이터를 필터링하거나 출력 형식을 변경할 수 있습니다.
        """

        add_exclude = set(["model_cls", "model"])
        if exclude:
            add_exclude = add_exclude | exclude
        return super().dict(
            include=include,
            exclude=add_exclude,
            by_alias=by_alias,
            exclude_unset=exclude_unset,
            exclude_defaults=exclude_defaults,
            exclude_none=exclude_none,
        )

    class Config:
        orm_mode = True
        use_enum_values = True
