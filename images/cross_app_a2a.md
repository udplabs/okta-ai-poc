Google Colab does not support directly embedding Mermaid!

The following diagram must be copy/pasted into https://mermaid.live and then you must generate a markdown link.

The following config is recommended:
```json
{
  "theme": "dark",
  "darkMode": true,
  "themeVariables": {
    "background": "#333"
  }
}
```

## Root Diagram
```mermaid
sequenceDiagram
    autonumber
    participant U as User

    box TRUST DOMAIN<br><br>Client / Agent J<br>
    participant C as Client App
    participant CAS as Authz Server
    participant A1 as Agent J
    end

    participant OAS as Okta Authz Server

    box TRUST DOMAIN<br><br>Agent K<br>
    participant A2 as Agent K
    participant A2AS as Authz Server
    end

    box TRUST DOMAIN<br><br>Resource<br>
    participant R as Resource
    participant RAS as Authz Server
    end

	rect rgb(0, 128, 255)
		Note over U, C: Step 1: Authenticate User
			U->>C: Authenticate<br>via browser
			C->>CAS: Authorization Code<br>+ Token request
			CAS-->>C: User access token
	end

    rect rgba(83, 156, 0, 1)
		Note over C, CAS: Step 2: API call w/ access token
		C->>A1: Request to Agent J w/ Access Token
		opt
			A1->>A1: Verify Access Token
		end
	end

	rect rgb(170, 0, 255)
		Note over A1: Step 3: Get an ID-JAG
			A1->>OAS: Exchange User Access Token<br>for ID-JAG targeting Agent K
			OAS-->>A1: ID-JAG Token
	end

	rect rgb(0, 156, 112)
		Note over A1: Step 4: Verify
		opt
			A1->>A1: Verify ID-JAG Token
		end
	end

	rect rgb(90, 49, 0)
		Note right of A1: Step 5: Exchange ID-JAG
			A1->>A2AS: Exchange ID-JAG for Agent K access token
			A2AS-->>A1: Access token
	end

	rect rgba(0, 86, 129, 1)
		Note over A1, OAS: Step 6: API call w/ access token
		A1->>A2: Request to Agent K w/ Access Token
		opt
			A2->>A2: Verify Access Token
		end
	end

	rect rgba(183, 0, 152, 1)
		Note over OAS, A2: Step 7: Get an ID-JAG
        A2->>OAS: Exchange access token for<br>ID-JAG targeting Resource
		OAS-->>A2: ID-JAG token
	end

	rect rgb(0, 156, 112)
		Note left of A2: Step 8: Verify
		opt
			A2->>A2: Verify ID-JAG Token
		end
	end

	rect rgb(255, 0, 119)
		Note over A2, A2AS: Step 9: Exchange ID-JAG
		A2->>RAS: Exchange ID-JAG for Resource access token
        RAS-->>A2: Access token
	end

	rect rgb(38, 73, 109)
		Note over A2, R: Step 10: API Call w/ access token
		A2-->>R: Request to Resource + Access Token
        R->>R: Validate access token
        R->>R: handle request
        R-->>A2: response
	end
```

## Step 1
```mermaid
sequenceDiagram
    autonumber
    participant U as User

    box TRUST DOMAIN<br><br>Client / Agent J<br>
    participant C as Client App
    participant CAS as Authz Server
    end

	rect rgb(0, 128, 255)
		Note over U, C: Step 1: Authenticate User
			U->>C: Authenticate<br>via browser
			C->>CAS: Authorization Code<br>+ Token request
			CAS-->>C: User access token
	end
```

## Step 2
```mermaid
sequenceDiagram
    autonumber 4

    box TRUST DOMAIN<br><br>Client / Agent J<br>
    participant C as Client App
    participant A1 as Agent J
    end

    rect rgba(83, 156, 0, 1)
		Note right of C: Step 2: API call w/ access token
		C->>A1: Request to Agent J w/ Access Token
		opt
			A1->>A1: Verify Access Token
		end
	end
```

## Step 3
```mermaid
sequenceDiagram
    autonumber 6

    participant A1 as Agent J

    participant OAS as Okta Authz Server

    rect rgb(170, 0, 255)
		Note over A1: Step 3: Get an ID-JAG
			A1->>OAS: Exchange User Access Token<br>for ID-JAG targeting Agent K
			OAS-->>A1: ID-JAG Token
	end
```

## Step 4
```mermaid
sequenceDiagram
    autonumber 8

    participant A1 as Agent J

	rect rgb(0, 156, 112)
		Note over A1: Step 4: Verify
		opt
			A1->>A1: Verify ID-JAG Token
		end
	end
```

## Step 5
```mermaid
sequenceDiagram
    autonumber 9

    box TRUST DOMAIN<br><br>Client / Agent J<br>
    participant A1 as Agent J
    end

    box TRUST DOMAIN<br><br>Agent K<br>

    participant A2AS as Authz Server
    end

	rect rgb(90, 49, 0)
		Note right of A1: Step 5: Exchange ID-JAG
			A1->>A2AS: Exchange ID-JAG for Agent K access token
			A2AS-->>A1: Access token
	end
```

## Step 6
```mermaid
sequenceDiagram
    autonumber 11

    box TRUST DOMAIN<br><br>Client / Agent J<br>
    participant A1 as Agent J
    end

    box TRUST DOMAIN<br><br>Agent K<br>
    participant A2 as Agent K
    end

	rect rgba(0, 86, 129, 1)
		Note over A1: Step 6: API call w/ access token
		A1->>A2: Request to Agent K w/ Access Token
		opt
			A2->>A2: Verify Access Token
		end
	end
```

## Step 7
```mermaid
sequenceDiagram
    autonumber 13

    participant OAS as Okta Authz Server

    box TRUST DOMAIN<br><br>Agent K<br>
    participant A2 as Agent K
    end

	rect rgba(183, 0, 152, 1)
		Note over OAS, A2: Step 7: Get an ID-JAG
        A2->>OAS: Exchange access token for<br>ID-JAG targeting Resource
		OAS-->>A2: ID-JAG token
	end

```

## Step 8
```mermaid
sequenceDiagram
    autonumber 15

    participant A2 as Agent K

	rect rgb(0, 156, 112)
		Note left of A2: Step 8: Verify
		opt
			A2->>A2: Verify ID-JAG Token
		end
	end
```

## Step 9
```mermaid
sequenceDiagram
    autonumber 16

    box TRUST DOMAIN<br><br>Agent K<br>
    participant A2 as Agent K
    end

    box TRUST DOMAIN<br><br>Resource<br>
    participant RAS as Authz Server
    end

	rect rgb(255, 0, 119)
		Note over A2: Step 9: Exchange ID-JAG
		A2->>RAS: Exchange ID-JAG for Resource access token
        RAS-->>A2: Access token
	end
```

## Step 10
```mermaid
sequenceDiagram
    autonumber 18

    box TRUST DOMAIN<br><br>Agent K<br>
    participant A2 as Agent K
    end

    box TRUST DOMAIN<br><br>Resource<br>
    participant R as Resource
    end

	rect rgb(38, 73, 109)
		Note over A2, R: Step 10: API Call w/ access token
		A2-->>R: Request to Resource + Access Token
        R->>R: Validate access token
        R->>R: handle request
        R-->>A2: response
	end
```