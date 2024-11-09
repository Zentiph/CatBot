"""
descriptions.py
File containing descriptions of commands to be used in help.py.
"""

from typing import (
    Any,
    Iterator,
    List,
    Literal,
    Type,
    Union,
    _SpecialForm,
    get_args,
    get_origin,
)


class _NoDefaultSentinel:
    """
    Sentinel for the NO_DEFAULT const.
    """

    __slots__ = ()

    def __eq__(self, other: object) -> bool:
        return isinstance(other, _NoDefaultSentinel)

    def __bool__(self) -> Literal[False]:
        return False

    def __hash__(self) -> Literal[0]:
        return 0

    def __repr__(self) -> Literal["..."]:
        return "..."


NO_DEFAULT: Any = _NoDefaultSentinel()


class Param:
    """
    Represents a slash command parameter.
    """

    # We use _SpecialForm here due to Literal not being a Type
    def __init__(  # pylint: disable=too-many-arguments
        self,
        *,
        name: str,
        type: Union[Type, _SpecialForm],  # pylint: disable=redefined-builtin
        description: str,
        optional: bool = False,
        default: Any = NO_DEFAULT,
    ) -> None:
        """
        Represents a slash command parameter.

        :param name: Name of the parameter
        :type name: str
        :param type: Type of the parameter
        :type type: Union[Type, _SpecialForm]
        :param description: Description of the parameter
        :type description: str
        :param optional: Whether the param is optional, defaults to False
        :type optional: bool, optional
        :param default: The param's default value, defaults to NO_DEFAULT
        :type default: Any, optional
        """

        self.__name = name
        self.__type = type
        self.__description = description
        self.__optional = optional
        self.__default = default

    @property
    def name(self) -> str:
        """
        :return: This Param's name
        :rtype: str
        """

        return self.__name

    @property
    def type(self) -> Union[Type, _SpecialForm]:
        """
        :return: This Param's type
        :rtype: Union[Type, _SpecialForm]
        """

        return self.__type

    @property
    def description(self) -> str:
        """
        :return: This Param's description
        :rtype: str
        """

        return self.__description

    @property
    def optional(self) -> bool:
        """
        :return: Whether this Param is optional
        :rtype: bool
        """

        return self.__optional

    @property
    def default(self) -> Any:
        """
        :return: This Param's default value
        :rtype: Any
        """

        return self.__default


class Command:
    """
    Represents a slash command.
    """

    def __init__(
        self, *, name: str, description: str, group: Union[str, None] = None
    ) -> None:
        """
        Represents a slash command.

        :param name: Command name
        :type name: str
        :param description: Command description
        :type description: str
        :param group: Command group this Command is in, defaults to None
        :type group: str | None
        """

        self.__name = name
        self.__description = description
        self.__params: List[Param] = []
        self.__current = 0
        self.__group = group

    def add_param(self, param: Param) -> None:
        """
        Add a param to the command.

        :param param: Param to add
        :type param: Param
        """

        if param.name in [param.name for param in self.__params]:
            raise AttributeError(f"Param {param.name} is already added to Command")

        self.__params.append(param)

    @property
    def name(self) -> str:
        """
        :return: Name of the command
        :rtype: str
        """

        return self.__name

    @property
    def description(self) -> str:
        """
        :return: Description of the command
        :rtype: str
        """

        return self.__description

    @property
    def group(self) -> Union[str, None]:
        """
        :return: Group of the command, if any
        :rtype: str, None
        """

        return self.__group

    @property
    def num_params(self) -> int:
        """
        :return: Number of params this Command has
        :rtype: int
        """

        return len(self.__params)

    def __iter__(self) -> Iterator[Param]:
        return self

    def __next__(self) -> Param:
        if self.__current >= len(self.__params):
            raise StopIteration

        self.__current += 1
        return self.__params[self.__current - 1]


# The idea is to format the commands into embed fields
# So, we have a title and description
# Thus we have these two functions:


def generate_field_title(command: Command, /) -> str:
    """
    Generate an embed field title given `command`.

    :param command: Command to generate a title for
    :type command: Command
    :return: Embed field title of `command`
    :rtype: str
    """

    if command.group is not None:
        return f"/{command.group} {command.name}"
    return f"/{command.name}"


def generate_field_description(command: Command) -> str:
    """
    Generate an embed field description given `command`.

    :param command: Command to generate a description for
    :type command: Command
    :return: Embed field description of `command`
    :rtype: str
    """

    field_str = f"{command.description}"

    if command.num_params > 0:
        field_str += "\nParameters:\n"

    for param in command:
        if get_origin(param.type) is Literal:  # If the param's type is a Literal
            values = get_args(param.type)
            types_str = "Specific Value(s): " + " or ".join(
                repr(value) for value in values
            )

        elif get_origin(param.type) is Union:  # Elif the param's type is a Union
            types_str = " or ".join(arg.__name__ for arg in get_args(param.type))

        else:  # Else, the type is a regular type
            # TODO: Create a map of type names in order to rename them
            #       to be more user friendly
            #
            #       i.e. str -> string or maybe text
            #            int -> integer
            #            float -> decimal or fraction
            #            NoneType -> no value
            types_str = param.type.__name__  # type: ignore

        optional_str = ", optional" if param.optional else ""
        default_str = (
            f", defaults to {repr(param.default)}"
            if param.default != NO_DEFAULT
            else ""
        )

        # Will look like:
        # {param_name} - {param_description}
        # ({param_type(s)}, {optional}, defaults to {param_default})
        field_str += (
            f"{param.name} - {param.description}\n"
            + f"({types_str}{optional_str}{default_str})\n"
        )

    return field_str.strip()
