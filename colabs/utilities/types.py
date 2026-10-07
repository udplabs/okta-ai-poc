from typing import Any, Literal, NotRequired, TypedDict


class LinkHints(TypedDict):
    allow: list[Literal["GET", "POST", "PUT", "DELETE", "PATCH"]]


class _Link(TypedDict):
    href: str
    rel: str
    name: NotRequired[str]
    hints: NotRequired[LinkHints]


class LinkSelf(TypedDict):
    self: _Link


class OidcAppAccessibility(TypedDict, total=False):
    selfService: bool
    errorRedirectUrl: str | None
    loginRedirectUrl: str | None


class OidcAppLinks(LinkSelf, total=False):
    uploadLogo: _Link
    appLinks: list[_Link]
    groups: _Link
    logo: list[_Link]
    users: _Link
    activate: _Link
    deactivate: _Link


class OidcAppVisibilityHide(TypedDict, total=False):
    iOS: bool
    web: bool


class OidcAppVisibility(TypedDict, total=False):
    autoLaunch: bool
    autoSubmitToolbar: bool
    hide: OidcAppVisibilityHide
    appLinks: dict[str, bool]


class OidcAppUserNameTemplate(TypedDict, total=False):
    template: str
    type: str


class OidcAppSigning(TypedDict, total=False):
    kid: str


class OidcAppOAuthCredentials(TypedDict):
    autoKeyRotation: bool
    client_id: str
    client_secret: str
    token_endpoint_auth_method: Literal[
        "client_secret_basic",
        "client_secret_post",
        "client_secret_jwt",
        "private_key_jwt",
        "none",
    ]
    pkce_required: bool


class OidcAppCredentials(TypedDict):
    userNameTemplate: NotRequired[OidcAppUserNameTemplate]
    signing: NotRequired[OidcAppSigning]
    oauthClient: OidcAppOAuthCredentials


class OidcAppIdpInitiatedLogin(TypedDict, total=False):
    mode: Literal["DISABLED", "SPECIFY_SCOPES"]
    default_scope: list[str]


class OidcAppOAuthSettings(TypedDict):
    client_uri: NotRequired[str]
    logo_uri: NotRequired[str]
    redirect_uris: list[str]
    post_logout_redirect_uris: NotRequired[list[str]]
    response_types: list[Literal["token", "id_token", "code"]]
    grant_types: list[str]
    application_type: Literal["web", "native", "browser", "service"]
    issuer_mode: Literal["ORG_URL", "CUSTOM_URL", "DYNAMIC"]
    idp_initiated_login: NotRequired[OidcAppIdpInitiatedLogin]
    wildcard_redirect: NotRequired[Literal["DISABLED", "SUBDOMAIN"]]
    dpop_bound_access_tokens: NotRequired[bool]


class OidcAppVpnNetwork(TypedDict, total=False):
    connection: Literal["DISABLED", "ANY", "ON_NETWORK", "OFF_NETWORK"]


class OidcAppVpn(TypedDict, total=False):
    network: OidcAppVpnNetwork
    message: str | None
    helpUrl: str | None


class OidcAppNotifications(TypedDict, total=False):
    vpn: OidcAppVpn


class OidcAppNotes(TypedDict, total=False):
    admin: str | None
    enduser: str | None


class OidcAppSettings(TypedDict):
    app: dict[str, Any]
    oauthClient: OidcAppOAuthSettings
    notifications: NotRequired[OidcAppNotifications]
    manualProvisioning: NotRequired[bool]
    implicitAssignment: NotRequired[bool]
    notes: NotRequired[OidcAppNotes]
    emOptInStatus: NotRequired[str]


class OidcApp(TypedDict):
    """Custom OIDC application JSON from the Okta Applications API.

    Nested types cover the response fields used in this guide and the sample.
    Optional keys may be absent; nullable values may explicitly be None.
    TypedDict provides static checking, not runtime validation or defaults.
    id, status, timestamps, orn, features, and _links are response metadata;
    omit them when building a create-application request.
    """

    name: Literal["oidc_client"]
    label: str
    signOnMode: Literal["OPENID_CONNECT"]
    id: str
    status: Literal["ACTIVE", "INACTIVE", "DELETED"]
    lastUpdated: str
    created: str
    orn: NotRequired[str]
    features: NotRequired[list[str]]
    accessibility: NotRequired[OidcAppAccessibility]
    _links: NotRequired[OidcAppLinks]
    visibility: NotRequired[OidcAppVisibility]
    credentials: OidcAppCredentials
    settings: OidcAppSettings
    profile: NotRequired[dict[str, Any]]


class AIAgentOAuthClient(TypedDict):
    client_id: str
    type: Literal["CIMD"]


class AIAgentSignOnProvider(TypedDict):
    appInstanceId: str


class AIAgentProfile(TypedDict):
    description: NotRequired[str]
    name: str | None
    externalId: NotRequired[str]
    platform: NotRequired[
        Literal[
            "AWS_BEDROCK_AGENTS",
            "AWS_BEDROCK_AGENTCORE",
            "SALESFORCE_AGENTFORCE",
            "GEMINI_ENTERPRISE_AGENT_PLATFORM",
            "MICROSOFT_COPILOT_STUDIO",
            "MICROSOFT_FOUNDRY",
            "SERVICENOW",
            "DATAROBOT_AGENT_WORKFORCE_PLATFORM",
            "CLAUDE_MANAGED_AGENTS",
            "WORKDAY_ASOR",
            "LANGSMITH_AGENTS",
            "DATABRICKS_GENIE_AGENTS",
            "DATABRICKS_AGENT_BRICKS",
            "TINES_AGENTS",
        ]
    ]


class _AIAgentLinks(LinkSelf):
    next: _Link | None
    resourceServer: NotRequired[_Link]
    delegationLinks: NotRequired[_Link]
    providers: NotRequired[_Link]


class AIResource(TypedDict):
    id: str
    status: Literal["ACTIVE", "INACTIVE", "STAGED"]
    type: Any
    _links: _AIAgentLinks


class A2AResource(AIResource):
    type: Literal["a2a-server-authorization-server"]


class WorkloadPrincipalResource(AIResource):
    type: Literal["ai_agent", "virtual_mcp"]


class Operation(TypedDict):
    id: str
    completed: NotRequired[str]
    created: str
    errorDetails: NotRequired[dict[str, Any]]
    started: NotRequired[str]
    status: Literal["COMPLETED", "SCHEDULED", "IN_PROGRESS", "FAILED"]
    type: Literal[
        "ai-agent:Register",
        "ai-agent:Replace",
        "ai-agent:Delete",
        "ai-agent:Activate",
        "ai-agent:Deactivate",
        "ai-agent:Patch",
        "ai-agent:Import",
        "virtual-mcp:Register",
        "virtual-mcp:Delete",
        "virtual-mcp:Activate",
        "virtual-mcp:ReplaceCapabilities",
        "ai-agent:Staging",
        "ai-agent:BulkStaging",
        "ai-agent:ReplaceSourcePriority",
    ]
    operationMetadata: NotRequired[dict[str, Any]]
    url: NotRequired[str]


class AIAgentOperation(Operation):
    resource: WorkloadPrincipalResource


class A2AResourceOperation(Operation):
    resource: A2AResource


class AIAgent(TypedDict, total=False):
    id: str
    created: str
    lastUpdated: str
    status: Literal["ACTIVE", "INACTIVE", "STAGED"]
    oauthClient: NotRequired[AIAgentOAuthClient]
    signOnProvider: NotRequired[AIAgentSignOnProvider]
    profile: NotRequired[AIAgentProfile]
    _links: _AIAgentLinks
    current_operation: AIAgentOperation
    resource_uri: str
    orn: str


class AuthorizationServerSigning(TypedDict):
    rotationMode: Literal["AUTO", "MANUAL"]
    lastRotated: str
    nextRotation: str
    kid: str


class AuthorizationServerLinks(LinkSelf):
    scopes: _Link
    claims: _Link
    policies: _Link
    metadata: list[_Link]
    rotateKey: _Link
    deactivate: _Link


class AuthorizationServerCredentials(TypedDict):
    signing: AuthorizationServerSigning


class AuthorizationServer(TypedDict):
    """Authorization Server JSON returned by the Okta Management API."""

    id: str
    name: str
    description: str
    audiences: list[str]
    issuer: str
    issuerMode: NotRequired[Literal["ORG_URL", "CUSTOM_URL", "DYNAMIC"]]
    status: Literal["ACTIVE", "INACTIVE"]
    created: str
    lastUpdated: str
    credentials: AuthorizationServerCredentials
    _links: AuthorizationServerLinks
    resource_access_policy_id: NotRequired[str]
    orn: NotRequired[str]


class A2AAuthorizationServerMetadata(TypedDict):
    authorizationEndpoint: str
    grantTypesSupported: list[str]
    tokenEndpoint: str


class A2AAuthorizationServer(TypedDict):
    id: str
    issuer: str
    lastUpdated: str
    orn: str
    status: Literal["ACTIVE", "INACTIVE", "INVALID"]
    _links: LinkSelf


class AIAgentState(AIAgent, total=False):
    resource_server: AuthorizationServer
    operation_url: str


class OidcAppState(TypedDict, total=False):
    app: OidcApp
    resource_server: AuthorizationServer


class CustomScope(TypedDict):
    id: str
    name: str
    description: str
    displayName: NotRequired[str]


class ResourceAuthorizationServerLinks(LinkSelf):
    web: NotRequired[_Link]


class ResourceConnectionAuthorizationServer(TypedDict):
    issuerUrl: str
    logo: NotRequired[str]
    name: str
    orn: str
    _links: ResourceAuthorizationServerLinks


class ResourceConnection(TypedDict):
    id: str
    orn: str
    status: Literal["ACTIVE", "INACTIVE"]
    resourceIndicator: NotRequired[str]
    scopeCondition: NotRequired[Literal["ALL_SCOPES", "INCLUDE_ONLY", "EXCLUDE"]]
    scopes: NotRequired[list[str]]
    _links: LinkSelf


class ResourceConnectionA2AResource(TypedDict):
    name: str
    orn: str
    _links: ResourceAuthorizationServerLinks


class ResourceConnectionsResponse(TypedDict):
    data: list[
        A2AResourceConnection
        | AppInstanceResourceConnection
        | AuthServerResourceConnection
    ]


class A2AResourceConnection(ResourceConnection):
    authorizationServer: ResourceConnectionAuthorizationServer
    connectionType: Literal["IDENTITY_ASSERTION_A2A_SERVER"]
    resource: ResourceConnectionA2AResource


class AppInstance(TypedDict):
    orn: str
    name: NotRequired[str]


class AppInstanceResourceConnection(ResourceConnection):
    connectionType: Literal["IDENTITY_ASSERTION_APP_INSTANCE"]
    appInstance: AppInstance
    clientIdAtResource: str


class AuthServerResourceConnection(ResourceConnection):
    connectionType: Literal["IDENTITY_ASSERTION_CUSTOM_AS"]
    authorizationServer: ResourceConnectionAuthorizationServer
