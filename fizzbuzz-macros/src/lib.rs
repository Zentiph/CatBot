use proc_macro::TokenStream;
use proc_macro2::TokenStream as TokenStream2;
use quote::quote;
use syn::{
    Error, Ident, ItemFn, LitStr, Result, Token,
    parse::{Parse, ParseStream},
};

/// A pair of parameter name and description.
///
/// # Fields
///
/// - `name` (`LitStr`) - The parameter name.
/// - `desc` (`LitStr`) - The parameter description.
struct ParamPair {
    name: LitStr,
    desc: LitStr,
}
impl Parse for ParamPair {
    fn parse(input: ParseStream) -> Result<Self> {
        let content;
        syn::parenthesized!(content in input);
        let name: LitStr = content.parse()?;
        let _: Token![,] = content.parse()?;
        let desc: LitStr = content.parse()?;
        // allow trailing comma inside the tuple
        if content.peek(Token![,]) {
            let _: Token![,] = content.parse()?;
        }
        Ok(ParamPair { name, desc })
    }
}

/// Arguments for the `command` macro.
///
/// # Fields
///
/// - `name` (`LitStr`) - The name of the command.
/// - `description` (`LitStr`) - The description of the command.
/// - `category` (`Ident`) - The category of the command.
/// - `params` (`Vec<ParamPair>`) - The parameters of the command.
/// - `examples` (`Option<Vec<LitStr>>`) - Examples of how to use the command.
/// - `notes` (`Option<Vec<LitStr>>`) - Any special notes about the command.
struct CommandArgs {
    name: LitStr,
    description: LitStr,
    category: Ident,
    params: Vec<ParamPair>,
    examples: Option<Vec<LitStr>>,
    notes: Option<Vec<LitStr>>,
}
impl Parse for CommandArgs {
    fn parse(input: ParseStream) -> Result<Self> {
        let mut name = None;
        let mut description = None;
        let mut category = None;
        let mut params = Vec::new();
        let mut examples = None;
        let mut notes = None;

        while !input.is_empty() {
            let key: Ident = input.parse()?;
            let _: Token![=] = input.parse()?;

            match key.to_string().as_str() {
                "name" => {
                    name = Some(input.parse::<LitStr>()?);
                }
                "description" => {
                    description = Some(input.parse::<LitStr>()?);
                }
                "category" => {
                    category = Some(input.parse::<Ident>()?);
                }
                "params" => {
                    let content;
                    syn::bracketed!(content in input);
                    while !content.is_empty() {
                        params.push(content.parse::<ParamPair>()?);
                        if content.peek(Token![,]) {
                            let _: Token![,] = content.parse()?;
                        }
                    }
                }
                "examples" => {
                    let content;
                    syn::bracketed!(content in input);
                    let mut list = Vec::new();
                    while !content.is_empty() {
                        list.push(content.parse::<LitStr>()?);
                        if content.peek(Token![,]) {
                            let _: Token![,] = content.parse()?;
                        }
                    }
                    examples = Some(list);
                }
                "notes" => {
                    let content;
                    syn::bracketed!(content in input);
                    let mut list = Vec::new();
                    while !content.is_empty() {
                        list.push(content.parse::<LitStr>()?);
                        if content.peek(Token![,]) {
                            let _: Token![,] = content.parse()?;
                        }
                    }
                    notes = Some(list);
                }
                other => {
                    return Err(Error::new(
                        key.span(),
                        format!(
                            "unknown key `{other}` — expected one of: name, description, category, params, examples, notes"
                        ),
                    ));
                }
            }

            if input.peek(Token![,]) {
                let _: Token![,] = input.parse()?;
            }
        }

        Ok(CommandArgs {
            name: name
                .ok_or_else(|| input.error("missing required key `name`"))?,
            description: description.ok_or_else(|| {
                input.error("missing required key `description`")
            })?,
            category: category.ok_or_else(|| {
                input.error("missing required key `category`")
            })?,
            params,
            examples,
            notes,
        })
    }
}

/// Implementation of the `command` macro.
///
/// # Arguments
///
/// - `args` (`TokenStream`) - The macro arguments (see `CommandArgs`).
/// - `item` (`TokenStream`) - The macro item.
///
/// # Returns
///
/// - `Result<TokenStream2>` - The original function with the command registered to inventory.
///
/// # Errors
///
/// Errors if the macro arguments are invalid.
fn command_impl(args: TokenStream, item: TokenStream) -> Result<TokenStream2> {
    let args = syn::parse::<CommandArgs>(args)?;
    let func: ItemFn = syn::parse(item)?;
    let fn_name = &func.sig.ident;

    let name_str = &args.name;
    let desc_str = &args.description;
    let category = &args.category;

    let param_tokens = args.params.iter().map(|p| {
        let n = &p.name;
        let d = &p.desc;
        quote! { (#n, #d) }
    });

    let examples_tokens = match &args.examples {
        None => quote! { None },
        Some(list) => quote! { Some(&[#(#list),*] as &[&str]) },
    };

    let notes_tokens = match &args.notes {
        None => quote! { None },
        Some(list) => quote! { Some(&[#(#list),*] as &[&str]) },
    };

    Ok(quote! {
        #func

        inventory::submit! {
            crate::discord::commands::Command {
                info: crate::discord::commands::CommandInfo {
                    name: #name_str,
                    description: #desc_str,
                    category: crate::discord::commands::CommandCategory::#category,
                    params: &[#(#param_tokens),*],
                    examples: #examples_tokens,
                    notes: #notes_tokens,
                },
                run: |ctx, cmd| ::std::boxed::Box::pin(#fn_name(ctx, cmd)),
            }
        }
    })
}

/// Register an async fn as a Discord slash command.
///
/// # Arguments
///
/// - `name` (required) — the slash command name, e.g. `"stats"`
/// - `description` (required) — shown in the Discord UI
/// - `category` (required) — a `CommandCategory` variant, e.g. `Misc`
/// - `params` (optional) — `[("param_name", "description"), ...]`
/// - `examples` (optional) — `["/stats", ...]`
/// - `notes` (optional) — `["Guild only", ...]`
///
/// # Example
///
/// ```rust
/// #[command(
///     name = "ping",
///     description = "Pong.",
///     category = Misc,
///     params = [("target", "Who to ping")],
///     examples = ["/ping @user"],
/// )]
/// async fn ping(ctx: &Context, interaction: &CommandInteraction) -> anyhow::Result<()> {
///     Ok(())
/// }
/// ```
#[proc_macro_attribute]
pub fn command(args: TokenStream, item: TokenStream) -> TokenStream {
    match command_impl(args, item) {
        Ok(tokens) => tokens.into(),
        Err(e) => e.to_compile_error().into(),
    }
}
